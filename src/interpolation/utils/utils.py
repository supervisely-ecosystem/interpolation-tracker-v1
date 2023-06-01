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
        raise ValueError("Can sort only polygons with same number of vertices.")

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


def obj_bbox(obj: np.ndarray):
    bot_right = (np.max(obj[:, 0]), np.min(obj[:, 1]))
    top_left = (np.min(obj[:, 0]), np.max(obj[:, 1]))
    center = np.mean([top_left, bot_right], axis=0)
    return top_left, bot_right, center

def shift_and_resize(obj1: np.ndarray, obj2: np.ndarray):
    o1_tl, o1_br, o1_center = obj_bbox(obj1)
    o2_tl, o2_br, o2_center = obj_bbox(obj2)
    shifted_o1 = obj1.copy() - o1_center
    shifted_o2 = obj2.copy() - o2_center

    o1_o2_ratio = np.array((
        abs(o1_tl[0] - o1_br[0]) / abs(o2_tl[0] - o2_br[0]),
        abs(o1_tl[1] - o1_br[1]) / abs(o2_tl[1] - o2_br[1]),
    ))

    shifted_o2 = shifted_o2 * o1_o2_ratio

    return shifted_o1, shifted_o2


def polygon_match(small_obj: np.ndarray, big_obj: np.ndarray):
    def cosin_sim_matrix(v1: np.ndarray, v2: np.ndarray, eps: float = 1e-8):
        dot_mat = v1 @ v2.T
        norm_prod_mat = np.linalg.norm(v1, axis=1)[:, None] @ np.linalg.norm(v2, axis=1)[None, :]
        return 1 - dot_mat / (norm_prod_mat + eps)
    
    # sgn = obj_order_sign(small_obj)
    # if sgn != obj_order_sign(big_obj):
    #     big_obj = big_obj[::-1]

    small_shifted, big_shifted = shift_and_resize(small_obj, big_obj)
    sim_mat = cosin_sim_matrix(small_shifted, big_shifted)

    mins = []
    start_i = None
    used = []

    for vec in sim_mat:
        min_i = np.argmin(vec)
        mins.append(min_i)
        if start_i is None:
            start_i = min_i
        else:
            if start_i > min_i:
                used = list(range(min_i))
                used.extend(list(range(start_i, len(big_obj))))
            else:
                used = list(range(start_i, min_i))
        sim_mat[:, used] = np.inf

    return {i: min_i for i, min_i in enumerate(mins)}


def add_points_to_obj_greedily(obj1: np.ndarray, obj2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    def calc_diff(prev, next, maxl):
        if prev > next:
            return maxl - prev + next
        return next - prev

    def uniform_points(point, next_point, num):
        dx = (next_point[0] - point[0]) / (num + 1)
        dy = (next_point[1] - point[1]) / (num + 1)
        points = []

        for i in range(1, num + 1):
            nx = point[0] + dx * i
            ny = point[1] + dy * i
            points.append([nx, ny])
        
        return points

    if len(obj1) > len(obj2):
        small_obj = obj2
        big_obj = obj1
        small_first = False
    elif len(obj1) < len(obj2):
        small_obj = obj1
        big_obj = obj2
        small_first = True
    else:
        return sort_for_interpolation(obj1, obj2)

    match_dct = polygon_match(small_obj, big_obj)
    
    sm_obj_ind = list(match_dct.keys())
    sm_obj_ind.append(sm_obj_ind[0])

    bg_obj_ind = list(match_dct.values())
    bg_obj_ind.append(bg_obj_ind[0])

    new_sm_obj = []
    new_bg_obj = []
    flag = False

    for l, r in zip(sm_obj_ind[:-1], sm_obj_ind[1:]):
        bl, br = match_dct[l], match_dct[r]
        diff = calc_diff(bl, br, len(big_obj))
        newpoints = []

        if diff == 1:
            if flag:
                flag = False
                new_sm_obj.append(small_obj[l])
                continue
            new_sm_obj.append(small_obj[l])
            new_bg_obj.append(big_obj[bl])
        elif diff == 0:
            if flag:
                new_sm_obj.append(small_obj[l])
                continue
            num = 0
            while bg_obj_ind[r] == bg_obj_ind[l]:
                num += 1
                r = (r + 1) % len(match_dct)

            newpoints = uniform_points(big_obj[bl], big_obj[(bl + 1) % len(big_obj)], num)
            new_sm_obj.append(small_obj[l])
            new_bg_obj.append(big_obj[bl])
            new_bg_obj.extend(newpoints)
            flag = True
        elif diff > 1:
            newpoints = uniform_points(small_obj[l], small_obj[r], diff - 1)
            new_sm_obj.append(small_obj[l])
            new_sm_obj.extend(newpoints)

            if flag:
                bl = (bl + 1) % len(big_obj)

            if bl > br:
                new_bg_obj.extend(big_obj[bl:])
                new_bg_obj.extend(big_obj[:br])
            else:
                new_bg_obj.extend(big_obj[bl:br])
            flag = False

    if small_first:
        return np.array(new_sm_obj), np.array(new_bg_obj)
    return np.array(new_bg_obj), np.array(new_sm_obj)
