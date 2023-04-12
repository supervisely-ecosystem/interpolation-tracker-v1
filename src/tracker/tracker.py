import bisect
from enum import Enum
from http import HTTPStatus
from collections import defaultdict
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from supervisely.geometry.geometry import Geometry


import sly_globals as g
from interpolation.base import BaseInterpolation

import supervisely_lib as sly


@dataclass
class ObjectInfo:
    frames: List[int] = field(default_factory=list)
    figures: List[Geometry] = field(default_factory=list)


class Direction(Enum):
    forward: int = 0
    backward: int = 1


class InterpolationTracker(object):
    direction_code = {
        "forward": Direction.forward,
        "backward": Direction.backward,
    }

    def __init__(self, context, interp_model: BaseInterpolation) -> None:
        self.interp_model = interp_model
        self.frame_index = context["frameIndex"]
        self.frames_count = context["frames"]

        self.track_id = context["trackId"]
        self.video_id = context["videoId"]
        self.objects_id = list(context["objectIds"])
        self.figure_ids = list(context["figureIds"])
        self.direction = self.direction_code[context["direction"]]

        last_or_first = self.frame_index + (-1) ** (self.direction.value) * self.frames_count
        self.last_index = max(last_or_first, self.frame_index)
        self.first_index = min(last_or_first, self.frame_index)

        if len(self.objects_id) < len(set(self.objects_id)):
            raise ValueError("Only one figure pre frame can be associated with a single object.")

        self.dataset_id = self.get_dataset_id()

        self.match_object_figures_on_frames()

    def get_dataset_id(self):
        oid = self.objects_id[0]
        obj_info = g.api.post("/annotation-objects.info", {"id": oid})
        return obj_info.json()["datasetId"]

    def match_object_figures_on_frames(self):
        # request info
        response = g.api.post("figures.list", data=self._make_filter())

        if response.status_code != HTTPStatus.OK:
            raise ValueError("Can't get figures info :(")

        figures_info = response.json()["entities"]
        object_frames_bounds = self._get_objects_frames_bounds()

        self.objects_info: Dict[int, ObjectInfo] = defaultdict(ObjectInfo)
        default_geometry = None
        for info in figures_info:
            oid = info["objectId"]
            left, right = object_frames_bounds[oid]
            frame = info["meta"]["frame"]

            if frame < left or frame > right:
                continue

            geometry_type = info["geometryType"]
            if default_geometry is None:
                default_geometry = geometry_type

            if default_geometry != geometry_type:
                raise ValueError(
                    f"All object's figures must be of the same geometry type: #{oid}-{default_geometry}",
                )

            geometry = info["geometry"]
            sly_fig = sly.deserialize_geometry(geometry_type, geometry)
            self.objects_info[oid].frames.append(frame)
            self.objects_info[oid].figures.append(sly_fig)
        self._check_figures()

    def track(self):
        for cur_pos, object_id in enumerate(self.objects_id, start=1):
            stop = self._track_obj(object_id, cur_pos)
            if stop:
                break

    def finish_tracking(self):
        self._notify(len(self.objects_id) + 1)

    def _get_objects_frames_bounds(self):
        resp = g.api.post(
            "videos.objects.get-frames",
            {
                "videoId": self.video_id,
                "objectIds": self.objects_id,
            },
        )
        bounds = {}
        for oid, frames in zip(self.objects_id, resp.json()):
            bounds[oid] = self._find_key_frames(frames)

        return bounds

    def _find_key_frames(self, frames: List[int]) -> Tuple[int, int]:
        sframes = sorted(frames)
        if self.direction is Direction.forward:
            start = self.first_index
            end_i = bisect.bisect_left(sframes, self.last_index)
            end_i = min(end_i, len(frames) - 1)
            end = sframes[end_i]
        else:
            end = self.last_index
            start_i = bisect.bisect_right(sframes, self.first_index) - 1
            start_i = max(0, start_i)
            start = sframes[start_i]
        return start, end

    def _make_filter(self):
        filter_fig = {"datasetId": self.dataset_id}
        filter_fig["filter"] = [
            {"field": "objectId", "operator": "in", "value": self.objects_id},
        ]
        filter_fig["fields"] = ["id", "objectId", "meta", "geometry", "geometryType"]
        return filter_fig

    def _notify(self, cur_pos: int) -> bool:
        # TODO: normal notification
        stop = g.api.video.notify_progress(
            self.track_id,
            self.video_id,
            self.first_index,
            self.last_index,
            cur_pos,
            len(self.objects_id) + 1,
        )

        return stop

    def _check_figures(self):
        for object_id in self.objects_id:
            frames = self.objects_info[object_id].frames

            if len(frames) < 2:
                if self.direction is Direction.forward:
                    msg = f"Skip interpolation for object #{object_id}: next frames don't have enough figures."
                else:
                    msg = f"Skip interpolation for object #{object_id}: previous frames don't have enough figures."

                g.logger.info(msg)
                raise ValueError(msg)

    def _track_obj(self, object_id: int, cur_pos: int) -> bool:
        frames = self.objects_info[object_id].frames
        figures = self.objects_info[object_id].figures

        sorted_fig_fr = sorted(zip(frames, figures), key=lambda pair: pair[0])
        sorted_frames = [p[0] for p in sorted_fig_fr]
        sorted_figures = [p[1] for p in sorted_fig_fr]

        start, end = min(frames), max(frames)
        all_frames = list(range(start, end + 1))

        # TODO: ask about full interpolation
        # all_frames = list(range(min(frames), max(frames)))

        interpol_geom = self.interp_model.interpolate(sorted_frames, sorted_figures, all_frames)

        for frame_index, geom in zip(all_frames, interpol_geom):
            if frame_index in frames:
                continue

            g.api.video.figure.create(
                self.video_id,
                object_id,
                frame_index,
                geometry_json=geom.to_json(),
                geometry_type=geom.geometry_name(),
                track_id=self.track_id,
            )

        stop = self._notify(cur_pos)
        return stop
