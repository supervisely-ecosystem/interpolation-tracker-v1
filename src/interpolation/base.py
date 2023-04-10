import numpy as np

from typing import List, Callable
from supervisely.geometry.geometry import Geometry


class BaseInterpolation(object):
    """Base class for interpolation.

    The main functions to be implemented:
        - geometry_to_numpy() - transforms Geometry (point, rectangle, polygon etc.)
            to numpy array with (n, 2) shape;
        - numpy_to_geometry() - transforms numpy array to Geometry;
        - one_point_coord_interpolation() - 1d-interpolation.
    """

    def __init__(self):
        self.figures = []
        self.meta = {}

    def interpolate(
        self, frames: List[int], figures: List[Geometry], all_frames: List[int]
    ) -> List[Geometry]:
        """Init interpolation function.

        Args:
            frames (List[int]): frames indices where the figure appears.
            figures (List[Geometry]): figures (1 per frame).
            all_frames (List[int]): The frames at which to evaluate the interpolated values.

        Returns:
            List[Geometry]: The interpolated Geometry, same length as `all_frames`.
        """
        self.figures = figures  # to use in geometry_to_numpy() if needed
        frames_with_figures = frames
        np_figures = [self.geometry_to_numpy(fig) for fig in figures]
        interpolation = self._create_vectorized_interpolation(all_frames, frames_with_figures)
        return self._interpolate(np_figures, interpolation)

    def geometry_to_numpy(self, obj: Geometry) -> np.ndarray:
        """Transform Geometry to npumpy array with (n, 2) shape."""
        raise NotImplementedError()

    def numpy_to_geometry(self, obj: np.ndarray) -> Geometry:
        """Transform numpy array to Geometry."""
        raise NotImplementedError

    def one_point_coord_interpolation(
        self,
        all_frames: List[int],
        frames_with_figures: List[int],
        coord_values: np.ndarray,
    ) -> np.ndarray:
        """Interpolate 1d

        Args:
            all_frames (List[int]): The frames at which to evaluate the interpolated values.
            frames_with_figures (List[int]): The frames idices of the data points.
            coord_values (np.ndarray): The position of the data points on frame,
                same length as `frames_with_figures`.
        Returns:
            np.ndarray: The interpolated values, same shape as `all_frames`.
        """
        raise NotImplementedError

    def _create_vectorized_interpolation(
        self, all_frames, frames_with_figures
    ) -> Callable[[np.ndarray], np.ndarray]:
        def interpolate(coord_values):
            return self.one_point_coord_interpolation(
                all_frames,
                frames_with_figures,
                coord_values,
            )

        return np.vectorize(interpolate, signature="(n)->(m)")

    def _interpolate(
        self,
        np_figures: List[np.ndarray],
        interpolation_func: Callable[[np.ndarray], np.ndarray],
    ) -> List[Geometry]:
        np_figures = np.array(np_figures)
        x_coords = np_figures[:, :, 0].T
        y_coords = np_figures[:, :, 1].T
        x_interp = interpolation_func(x_coords)
        y_interp = interpolation_func(y_coords)
        frames_count = x_interp.shape[1]

        def fin_vector(frame_idx):
            x = x_interp[:, frame_idx]
            y = y_interp[:, frame_idx]
            return np.vstack((x, y)).T

        interp_v = []

        for idx in range(frames_count):
            geom = self.numpy_to_geometry(fin_vector(idx))
            interp_v.append(geom)

        return interp_v
