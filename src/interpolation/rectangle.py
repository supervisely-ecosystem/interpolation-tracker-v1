import numpy as np

from typing import List
from interpolation.base import BaseRectangleInterpolation
from supervisely import Rectangle


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
