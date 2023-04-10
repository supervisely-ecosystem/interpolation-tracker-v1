import numpy as np

from typing import List
from supervisely.geometry.geometry import Geometry
from supervisely import Rectangle

from interpolation.base import BaseInterpolation


class BaseRectangleInterpolation(BaseInterpolation):
    def geometry_to_numpy(self, obj: Geometry) -> np.ndarray:
        if not isinstance(obj, Rectangle):
            raise TypeError("Can interpolate only Rectangles.")

        left_top = [obj.left, obj.top]
        right_bottom = [obj.right, obj.bottom]

        return np.array([left_top, right_bottom])

    def numpy_to_geometry(self, obj: np.ndarray) -> Geometry:
        left_top = obj[0].astype(int)
        right_bottom = obj[1].astype(int)
        fig = Rectangle(
            top=left_top[1],
            left=left_top[0],
            bottom=right_bottom[1],
            right=right_bottom[0],
        )
        return fig


class LinearRectangleInterpolation(BaseRectangleInterpolation):
    def one_point_coord_interpolation(
        self,
        all_frames: List[int],
        frames_with_figures: List[int],
        coord_values: np.ndarray,
    ) -> np.ndarray:
        return np.interp(all_frames, frames_with_figures, coord_values)


def main():
    figures = [Rectangle(0, 10, 10, 20), Rectangle(10, 20, 33, 35)]
    model = LinearRectangleInterpolation()
    int = model.interpolate([3, 6], figures, [3, 4, 5, 6])
    print(len(int))


if __name__ == "__main__":
    main()
