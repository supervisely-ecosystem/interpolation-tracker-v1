from collections import namedtuple
import functools

import sly_globals as g
import supervisely_lib as sly

from tracker import InterpolationTracker
from interpolation import (
    LinearPolygonInterpolation,
    LinearRectangleInterpolation,
    LinearPointInterpolation,
)

ContextTypes = namedtuple("ContextTypes", ["points", "polygons", "rectangles"])


def send_error_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = None
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            track_id = kwargs["context"]["trackId"]
            g.api.post(
                "videos.notify-annotation-tool",
                data={
                    "type": "videos:tracking-error",
                    "data": {"trackId": track_id, "error": {"message": repr(e)}},
                },
            )
        return value

    return wrapper


@g.my_app.callback("ping")
@sly.timeit
@send_error_data
def get_session_info(api: sly.Api, task_id, context, state, app_logger):
    pass


@g.my_app.callback("track")
@sly.timeit
@send_error_data
def track(api: sly.Api, task_id, context, state, app_logger):
    devided_context: ContextTypes = parse_context(api, context)

    if devided_context.polygons is not None:
        model = LinearPolygonInterpolation(g.shape_complexity)
        tracker = InterpolationTracker(devided_context.polygons, model)
        tracker.track()

    if devided_context.rectangles is not None:
        model = LinearRectangleInterpolation()
        tracker = InterpolationTracker(devided_context.rectangles, model)
        tracker.track()

    if devided_context.points is not None:
        model = LinearPointInterpolation()
        tracker = InterpolationTracker(devided_context.points, model)
        tracker.track()

    tracker.finish_tracking()
    return


def parse_context(api: sly.Api, context) -> ContextTypes:
    figures = context["figureIds"]
    points, polygons, rectangles = set(), set(), set()

    points_context = None
    rectangles_context = None
    polygons_context = None

    for fig_id in figures:
        fig = api.video.figure.get_info_by_id(fig_id)
        geometry = fig.geometry_type
        oid = fig.object_id

        if geometry == "polygon":
            polygons.add(oid)
        elif geometry == "rectangle":
            rectangles.add(oid)
        elif geometry == "point":
            points.add(oid)
        else:
            raise ValueError(f"Geometry type {geometry} is not supported by this app.")

    if len(points) > 0:
        points_context = context.copy()
        points_context["objectIds"] = list(points)

    if len(rectangles) > 0:
        rectangles_context = context.copy()
        rectangles_context["objectIds"] = list(rectangles)

    if len(polygons) > 0:
        polygons_context = context.copy()
        polygons_context["objectIds"] = list(polygons)

    return ContextTypes(
        points=points_context, polygons=polygons_context, rectangles=rectangles_context
    )


def main():
    sly.logger.info(
        "Script arguments",
        extra={"context.teamId": g.team_id, "context.workspaceId": g.workspace_id},
    )
    g.my_app.run()


if __name__ == "__main__":
    sly.main_wrapper("main", main)
