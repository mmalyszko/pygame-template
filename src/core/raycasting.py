import math
from typing import NamedTuple, Protocol


class WallGrid(Protocol):
    def is_wall(self, x: int, y: int) -> bool: ...


class RayHit(NamedTuple):
    depth: float
    x: float
    y: float
    is_vertical: bool
    angle: float


def texture_offset(hit: RayHit) -> float:
    # texture sampling direction depends on the ray's angle and whether it hit a vertical
    # or horizontal wall - without it, textures are mirrored depending on approach side
    if hit.is_vertical:
        frac = hit.y % 1
        return frac if math.cos(hit.angle) > 0 else 1 - frac
    frac = hit.x % 1
    return (1 - frac) if math.sin(hit.angle) > 0 else frac


EPSILON = 1e-6
MAX_DEPTH_TILES = 32


class Raycaster:
    def __init__(self, wall_grid: WallGrid):
        self.wall_grid = wall_grid

    def cast_single_ray(self, origin_x: float, origin_y: float, angle: float) -> RayHit:
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)

        vert_depth, vert_x, vert_y = self._get_vertical_intersection(origin_x, origin_y, sin_a, cos_a)
        hor_depth, hor_x, hor_y = self._get_horizontal_intersection(origin_x, origin_y, sin_a, cos_a)

        if vert_depth < hor_depth:
            return RayHit(vert_depth, vert_x, vert_y, True, angle)
        return RayHit(hor_depth, hor_x, hor_y, False, angle)

    def cast_rays_fan(self, origin_x: float, origin_y: float, angle: float, fov: float, num_rays: int) -> list[RayHit]:
        half_fov_tan = math.tan(fov / 2)
        hits = []

        for i in range(num_rays):
            camera_x = 2 * i / (num_rays - 1) - 1
            theta = math.atan(camera_x * half_fov_tan)
            hit = self.cast_single_ray(origin_x, origin_y, angle + theta)
            fixed_depth = hit.depth * math.cos(theta)  # fisheye fix
            hits.append(RayHit(fixed_depth, hit.x, hit.y, hit.is_vertical, hit.angle))

        return hits

    def _get_vertical_intersection(
        self, ox: float, oy: float, sin_a: float, cos_a: float
    ) -> tuple[float, float, float]:
        if abs(cos_a) < EPSILON:
            return math.inf, ox, oy

        step_x = 1 if cos_a > 0 else -1
        x = math.floor(ox) + 1 if cos_a > 0 else math.floor(ox) - EPSILON

        depth = (x - ox) / cos_a
        y = oy + depth * sin_a

        delta_depth = step_x / cos_a
        delta_y = delta_depth * sin_a

        for _ in range(MAX_DEPTH_TILES):
            if self.wall_grid.is_wall(math.floor(x), math.floor(y)):
                break
            x += step_x
            y += delta_y
            depth += delta_depth

        return depth, x, y

    def _get_horizontal_intersection(
        self, ox: float, oy: float, sin_a: float, cos_a: float
    ) -> tuple[float, float, float]:
        if abs(sin_a) < EPSILON:
            return math.inf, ox, oy

        step_y = 1 if sin_a > 0 else -1
        y = math.floor(oy) + 1 if sin_a > 0 else math.floor(oy) - EPSILON

        depth = (y - oy) / sin_a
        x = ox + depth * cos_a

        delta_depth = step_y / sin_a
        delta_x = delta_depth * cos_a

        for _ in range(MAX_DEPTH_TILES):
            if self.wall_grid.is_wall(math.floor(x), math.floor(y)):
                break
            x += delta_x
            y += step_y
            depth += delta_depth

        return depth, x, y
