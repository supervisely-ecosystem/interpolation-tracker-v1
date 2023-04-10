import numpy as np
from typing import List, Tuple, Dict
from collections import namedtuple


def min_dist(obj: np.ndarray) -> float:
    """Calculate min length of edge.

    Args:
        obj (np.ndarray): polygon points in clockwise or anticlockwise order.

    Returns:
        float: minimum edge length
    """
    return np.min(np.linalg.norm((np.roll(obj, -1, axis=0) - obj), axis=1))


def rm_points(obj: np.ndarray, min_d: float, new_per_side: int) -> np.ndarray:
    """Remove edges with length < `min_d`.

    Args:
        obj (np.ndarray): polygon points in clockwise or anticlockwise order.
        min_d (float): minimum edge length.
        new_per_side (int): 0 and every `new_per_side + 1` dots will not be removed.

    Returns:
        np.ndarray: polygon without deleted edges (points).
    """
    vp = obj[0]
    new_obj = [vp]
    point_idx = 0

    for vn in obj[1:]:
        point_idx += 1
        d = np.linalg.norm(vn - vp)
        if d < min_d and point_idx <= new_per_side:
            continue
        new_obj.append(vn)
        vp = vn

        if point_idx > new_per_side:
            point_idx = 0

    return np.array(new_obj)


def obj_order_sign(obj: List[List[float]]) -> int:
    """Find the sort (order) sign: `1` for clockwise, `-1` for anticlockwise.

    Args:
        obj (List[List[float]]): polygon points in clockwise or anticlockwise order.

    Returns:
        int: order sign.
    """
    ord_obj = [[*point, i] for i, point in enumerate(obj)]
    ord_obj = sorted(ord_obj, key=lambda x: (x[1], -x[0]))
    start_i = ord_obj[0][-1]

    if start_i == len(obj) - 1:
        next_i = 0
    else:
        next_i = start_i + 1

    prev_i = start_i - 1

    vert_s = np.array(obj[start_i])
    vert_p = np.array(obj[prev_i])
    vert_n = np.array(obj[next_i])

    vec1 = np.append(vert_p - vert_s, 0)
    vec2 = np.append(vert_n - vert_s, 0)

    return np.sign(np.cross(vec1, vec2)[-1])


def sort_for_interpolation(obj1: np.ndarray, obj2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Sorts (shift) circularly to minimize total distances between matching points.
        The number of polygon points must be the same for `obj1` and `obj2`
        and have equal order sign.

    Args:
        obj1 (np.ndarray): polygon points in clockwise or anticlockwise order.
        obj2 (np.ndarray): polygon points in clockwise or anticlockwise order.

    Returns:
        Tuple[np.ndarray, np.ndarray]: sorted polygons.
    """
    if obj1.shape[0] != obj2.shape[0]:
        raise ValueError("Can sort only poligons with same number of vertices.")

    min_d = np.inf
    shift = 0
    for i in range(len(obj1)):
        d = np.sum(np.linalg.norm(np.roll(obj1, -i, axis=0) - obj2, axis=1))
        if min_d > d:
            shift = -i
            min_d = d

    return np.roll(obj1, shift, axis=0), obj2


def add_points_to_obj(obj: np.ndarray, total_points: int) -> np.ndarray:
    """Adds `total_points // len(obj)` points to each edge.

    Args:
        obj (np.ndarray): polygon points in clockwise or anticlockwise order.
        total_points (int): total number of points to add.

    Raises:
        ValueError: `total_points // len(obj)` must be integer.

    Returns:
        np.ndarray: polygon with new points in clockwise or anticlockwise order.
    """
    if total_points <= 0:
        return obj

    if total_points % len(obj) != 0:
        raise ValueError("You can only add the same number of points on each edge.")

    per_edge = total_points // len(obj)
    start_point = list(obj[0])
    new_obj = [start_point]

    for point in list(np.roll(obj, -1, axis=0)):
        dx = (point[0] - start_point[0]) / (per_edge + 1)
        dy = (point[1] - start_point[1]) / (per_edge + 1)
        for step in range(1, per_edge + 1):
            nx = start_point[0] + step * dx
            ny = start_point[1] + step * dy
            new_obj.append([nx, ny])
        new_obj.append(point)
        start_point = point

    return np.array(new_obj[:-1])


def add_points_to_obj_greedly(obj1: np.ndarray, obj2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    PosDist = namedtuple("PosDist", ["pos", "dist"])

    if len(obj1) > len(obj2):
        bg_obj, sm_obj = obj1.copy(), obj2.copy()
        target = obj2
        target_str = "obj2"
    elif len(obj2) > len(obj1):
        bg_obj, sm_obj = obj2.copy(), obj1.copy()
        target = obj1
        target_str = "obj1"
    else:
        return obj1, obj2

    sm_bg_index_dct: Dict[int, PosDist] = {pos: PosDist(-1, np.inf) for pos in range(len(sm_obj))}
    used_bg_ind = set()
    bg_obj = move_to_axis_begin(bg_obj)
    sm_obj = move_to_axis_begin(sm_obj)

    for sm_i, point in enumerate(sm_obj):
        for bg_i, nearest_point in enumerate(bg_obj):
            dist = np.linalg.norm(point - nearest_point)
            if sm_bg_index_dct[sm_i].dist > dist and bg_i not in used_bg_ind:
                sm_bg_index_dct[sm_i] = PosDist(bg_i, dist)
        used_bg_ind.add(sm_bg_index_dct[sm_i].pos)
        # bg_sm_index_dct[sm_bg_index_dct[sm_i].pos] = sm_i

    new_sm_obj = []
    prev_i, prev_point = 0, target[0]

    def calc_diff(prev_i, next_i, obj_len):
        if prev_i < next_i:
            return abs(prev_i - next_i)
        return obj_len - prev_i + next_i

    for sm_i, point in enumerate(np.roll(target, -1, axis=0), start=1):
        sm_i = sm_i % len(sm_obj)
        diff = calc_diff(sm_bg_index_dct[prev_i].pos, sm_bg_index_dct[sm_i].pos, len(bg_obj))

        if diff < 1:
            raise ValueError("Smth goes wrong.")
        elif diff == 1:
            new_sm_obj.append(list(point))
            prev_point = point
            prev_i = sm_i
            continue

        dx = (point[0] - prev_point[0]) / diff
        dy = (point[1] - prev_point[1]) / diff

        for i in range(1, diff):
            nx = prev_point[0] + dx * i
            ny = prev_point[1] + dy * i
            new_sm_obj.append([nx, ny])

        new_sm_obj.append(list(point))
        prev_point = point
        prev_i = sm_i

    if target_str == "obj1":
        return np.array(new_sm_obj), obj2
    return obj1, np.array(new_sm_obj)


def move_to_axis_begin(obj: np.ndarray) -> np.ndarray:
    x_shift = min(obj[:, 0])
    y_shift = min(obj[:, 1])

    obj[:, 0] -= x_shift
    obj[:, 1] -= y_shift

    return obj
