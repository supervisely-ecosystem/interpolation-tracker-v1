import numpy as np
from typing import List
from supervisely.geometry.geometry import Geometry
from supervisely import Polygon, PointLocation

from interpolation.base import BaseInterpolation
from interpolation.utils import (
    obj_order_sign,
    min_dist,
    add_points_to_obj,
    rm_points,
    sort_for_interpolation,
)


class BasePolygonInterpolation(BaseInterpolation):
    def numpy_to_geometry(self, obj: np.ndarray) -> Geometry:
        obj = rm_points(obj, self._min_d, self._new_per_side)
        obj = obj.astype(int)
        exterior = [PointLocation(*obj_point) for obj_point in obj]
        return Polygon(exterior=exterior)

    def geometry_to_numpy(self, obj: Geometry) -> np.ndarray:
        if not isinstance(obj, Polygon):
            raise ValueError("Use only for polygons.")
        if len(obj.interior) > 0:
            raise ValueError("Can't interpolate objects with holles.")
        cur_sgn = obj_order_sign(obj.exterior_np)
        if cur_sgn == self._sgn:
            return obj.exterior_np
        return obj.exterior_np[::-1]

    def interpolate(
        self, frames: List[int], figures: List[Geometry], all_frames: List[int]
    ) -> List[Geometry]:
        fig1 = figures[0]

        if not isinstance(fig1, Polygon):
            raise ValueError("Use only for polygons.")

        self._sgn = obj_order_sign(fig1.exterior_np)
        figures_np = [self.geometry_to_numpy(fig) for fig in figures]
        fig_pairs = zip(figures_np[:-1], figures_np[1:])
        frame_pairs = zip(frames[:-1], frames[1:])
        interp_geoms = [figures[0]]

        for figs_p, frm_p in zip(fig_pairs, frame_pairs):
            start_frame, end_frame = frm_p
            start_fig, end_fig = figs_p

            start_len, end_len = len(start_fig), len(end_fig)
            self._min_d = min(min_dist(start_fig), min_dist(end_fig))

            # create points for
            lcm_len = np.lcm(start_len, end_len)
            start_total_points = lcm_len - start_len
            end_total_points = lcm_len - end_len
            self._new_per_side = min(start_total_points // start_len, end_total_points // end_len)
            start_fig = add_points_to_obj(start_fig, start_total_points)
            end_fig = add_points_to_obj(end_fig, end_total_points)

            # sort
            start_fig, end_fig = sort_for_interpolation(start_fig, end_fig)

            # interpolate
            interpolation = self._create_vectorized_interpolation(
                list(range(start_frame, end_frame + 1)), frm_p
            )
            interp_geoms.extend(self._interpolate([start_fig, end_fig], interpolation)[1:])

        return interp_geoms


class LinearPolygonInterpolation(BasePolygonInterpolation):
    def one_point_coord_interpolation(
        self,
        all_frames: List[int],
        frames_with_figures: List[int],
        coord_values: np.ndarray,
    ) -> np.ndarray:
        return np.interp(all_frames, frames_with_figures, coord_values)
