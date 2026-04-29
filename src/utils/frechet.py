from __future__ import annotations
import math
from typing import List, Tuple

Point = Tuple[float, float]
Path = List[Point]


def _euclidean(p: Point, q: Point) -> float:
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def frechet_distance(path_a: Path, path_b: Path) -> float:
    if len(path_a) < 2 or len(path_b) < 2:
        raise ValueError(
            f"Her iki yol da en az 2 nokta içermelidir. "
            f"Verilen: path_a={len(path_a)}, path_b={len(path_b)}"
        )

    n = len(path_a)
    m = len(path_b)
    ca: List[List[float]] = [[-1.0] * m for _ in range(n)]

    def _dp(i: int, j: int) -> float:
        if ca[i][j] > -1:
            return ca[i][j]
        d = _euclidean(path_a[i], path_b[j])
        if i == 0 and j == 0:
            ca[i][j] = d
        elif i == 0:
            ca[i][j] = max(_dp(0, j - 1), d)
        elif j == 0:
            ca[i][j] = max(_dp(i - 1, 0), d)
        else:
            ca[i][j] = max(
                min(_dp(i - 1, j), _dp(i - 1, j - 1), _dp(i, j - 1)),
                d,
            )
        return ca[i][j]

    return _dp(n - 1, m - 1)


def _flatten_detection(detection: dict) -> dict:
    bbox = detection.get("boundingBox")
    if bbox and isinstance(bbox, dict):
        return {
            "left":   bbox.get("left",   0),
            "top":    bbox.get("top",    0),
            "width":  bbox.get("width",  0),
            "height": bbox.get("height", 0),
        }
    return {
        "left":   detection.get("left",   detection.get("x", 0)),
        "top":    detection.get("top",    detection.get("y", 0)),
        "width":  detection.get("width",  0),
        "height": detection.get("height", 0),
    }


def get_anchor_point(detection: dict, anchor: str = "CENTER") -> Point:
    flat   = _flatten_detection(detection)
    left   = flat["left"]
    top    = flat["top"]
    width  = flat["width"]
    height = flat["height"]

    cx = left + width  / 2.0
    cy = top  + height / 2.0

    mapping = {
        "CENTER":        (cx,           cy),
        "BOTTOM_CENTER": (cx,           top + height),
        "TOP_CENTER":    (cx,           top),
        "CENTER_LEFT":   (left,         cy),
        "CENTER_RIGHT":  (left + width, cy),
    }

    return mapping.get(anchor.upper(), (cx, cy))