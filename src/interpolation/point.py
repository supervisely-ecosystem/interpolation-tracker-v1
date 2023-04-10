import numpy as np
from typing import List
from supervisely.geometry.geometry import Geometry
from supervisely import Point

from interpolation.base import BaseInterpolation


class BasePointInterpolation(BaseInterpolation):
    def geometry_to_numpy(self, obj: Geometry) -> np.ndarray:
        if not isinstance(obj, Point):
            raise TypeError("Can interpolate only Points.")
        return np.array([[obj.row, obj.col]])

    def numpy_to_geometry(self, obj: np.ndarray) -> Geometry:
        row, col = obj.squeeze()
        return Point(row=row, col=col)


class LinearPointInterpolation(BasePointInterpolation):
    def one_point_coord_interpolation(
        self,
        all_frames: List[int],
        frames_with_figures: List[int],
        coord_values: np.ndarray,
    ) -> np.ndarray:
        return np.interp(all_frames, frames_with_figures, coord_values)
