import math

import pygame

from src.core.raycasting import RayHit
from src.core.viewport import Viewport
from src.game.level import Level
from src.game.objects import Player

VIEWPORT_COLS = 8
VIEWPORT_ROWS = 8
MINIMAP_TILE_SIZE = 18
TARGET_NUM_RAYS = 60
BACKGROUND_COLOR = (10, 10, 15)
GRID_COLOR = (60, 60, 70)
WALL_COLOR = (150, 150, 150)
RAY_COLOR = (255, 255, 0, 90)
PLAYER_COLOR = (220, 40, 40)
PLAYER_DIRECTION_LENGTH_TILES = 2


class Minimap:
    def __init__(self):
        self.surface = pygame.Surface((VIEWPORT_COLS * MINIMAP_TILE_SIZE, VIEWPORT_ROWS * MINIMAP_TILE_SIZE))

    def render(self, level: Level, player: Player, hits: list[RayHit]) -> pygame.Surface:
        viewport = Viewport(level.cols, level.rows, VIEWPORT_COLS, VIEWPORT_ROWS)
        viewport.center_on(player.center_x, player.center_y)

        self.surface.fill(BACKGROUND_COLOR)

        self._render_grid()
        self._render_walls(level, viewport)
        self._render_rays(player, viewport, hits)
        self._render_player(player, viewport)

        return self.surface

    def _to_pixels(self, viewport: Viewport, world_x: float, world_y: float) -> tuple[int, int]:
        x, y = viewport.world_to_viewport(world_x, world_y, MINIMAP_TILE_SIZE)
        return int(x), int(y)

    def _render_grid(self) -> None:
        width, height = self.surface.get_size()
        for col in range(VIEWPORT_COLS + 1):
            x = col * MINIMAP_TILE_SIZE
            pygame.draw.line(self.surface, GRID_COLOR, (x, 0), (x, height))
        for row in range(VIEWPORT_ROWS + 1):
            y = row * MINIMAP_TILE_SIZE
            pygame.draw.line(self.surface, GRID_COLOR, (0, y), (width, y))

    def _render_walls(self, level: Level, viewport: Viewport) -> None:
        first_col = math.floor(viewport.offset_x)
        first_row = math.floor(viewport.offset_y)
        for tile_y in range(first_row, first_row + VIEWPORT_ROWS + 1):
            for tile_x in range(first_col, first_col + VIEWPORT_COLS + 1):
                if not level.is_wall(tile_x, tile_y):
                    continue
                x, y = self._to_pixels(viewport, tile_x, tile_y)
                rect = pygame.Rect(x, y, MINIMAP_TILE_SIZE, MINIMAP_TILE_SIZE)
                pygame.draw.rect(self.surface, WALL_COLOR, rect)

    def _render_rays(self, player: Player, viewport: Viewport, hits: list[RayHit]) -> None:
        origin_point = self._to_pixels(viewport, player.center_x, player.center_y)
        stride = max(1, len(hits) // TARGET_NUM_RAYS)  # reduces number of rays on minimap
        # drawing transparent rays require a separate surface
        ray_surface = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        for hit in hits[::stride]:  # reuse existing hits from core raycaster
            hit_point = self._to_pixels(viewport, hit.x, hit.y)
            pygame.draw.line(ray_surface, RAY_COLOR, origin_point, hit_point, 1)
        self.surface.blit(ray_surface, (0, 0))

    def _render_player(self, player: Player, viewport: Viewport) -> None:
        center = self._to_pixels(viewport, player.center_x, player.center_y)

        pygame.draw.circle(self.surface, PLAYER_COLOR, center, MINIMAP_TILE_SIZE // 4)

        direction_end = self._to_pixels(
            viewport,
            player.center_x + math.cos(player.angle) * PLAYER_DIRECTION_LENGTH_TILES,
            player.center_y + math.sin(player.angle) * PLAYER_DIRECTION_LENGTH_TILES,
        )
        pygame.draw.line(self.surface, PLAYER_COLOR, center, direction_end, 2)
