import math
from pathlib import Path

import pygame

from src.core.raycasting import Raycaster, RayHit, texture_offset
from src.game.level import Level
from src.game.minimap import Minimap
from src.game.objects import Player

FOV = math.pi / 3
STRIP_WIDTH = 2  # 1 cast ray == 2 screen pixels == 1 texture column

MIN_DEPTH = 0.0001  # prevents division by near-zero on very small ray depth
SHADE_START_DEPTH = 1.5  # shading starts after this depth
MAX_SHADE_DEPTH = 16  # shading stops at this depth with MIN_SHADE
MIN_SHADE = 0.4  # 0 = black, 1 = no darkening
HORIZONTAL_SHADE_MULTIPLIER = 0.8  # horizontal-facing walls differs a little in brightness
SHADE_LEVELS = 16  # precomputed textures copies for simple distance-shading

FLOOR_FAKE_PLAYER_Z = 0.5  # for the floor's distance-shading only
FLOOR_SHADE_FALLOFF = 0.07  # higher == floor darkens faster with distance

FLOOR_COLOR = (60, 60, 60)
WALL_COLOR_VERTICAL = (170, 130, 90)
WALL_COLOR_HORIZONTAL = (140, 105, 70)

TEXTURE_SIZE = 256
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def brightness_for_depth(depth: float) -> float:
    if depth <= SHADE_START_DEPTH:
        return 1.0
    falloff_range = MAX_SHADE_DEPTH - SHADE_START_DEPTH
    return max(MIN_SHADE, 1 - (depth - SHADE_START_DEPTH) / falloff_range)


def brightness_level_for_depth(depth: float, is_vertical: bool) -> int:
    brightness = brightness_for_depth(depth)
    if not is_vertical:
        brightness *= HORIZONTAL_SHADE_MULTIPLIER
    level = round((brightness - MIN_SHADE) / (1 - MIN_SHADE) * (SHADE_LEVELS - 1))
    return max(0, min(SHADE_LEVELS - 1, level))


def shaded_color(color: tuple[int, int, int], depth: float) -> tuple[int, int, int]:
    brightness = brightness_for_depth(depth)
    return int(color[0] * brightness), int(color[1] * brightness), int(color[2] * brightness)


class Renderer:
    use_shading = True
    use_textures = True
    show_minimap = True

    def __init__(self, screen: pygame.Surface, raycaster: Raycaster):
        self.screen = screen
        self.raycaster = raycaster
        self.minimap = Minimap()
        self.is_ready = False

    def load_resources(self) -> None:
        self.wall_texture = self._load_texture("wall.png")
        self.shaded_wall_textures = self._precompute_shades(self.wall_texture)
        self.sky_texture = self._load_sky_texture("sky.png")
        self.is_ready = True

    def _load_texture(self, filename: str) -> pygame.Surface:
        texture = pygame.image.load(str(DATA_DIR / filename)).convert()
        return pygame.transform.scale(texture, (TEXTURE_SIZE, TEXTURE_SIZE))

    def _load_sky_texture(self, filename: str) -> pygame.Surface:
        texture = pygame.image.load(str(DATA_DIR / filename)).convert()
        half_height = self.screen.get_height() // 2
        return pygame.transform.scale(texture, (texture.get_width(), half_height))

    def _precompute_shades(self, texture: pygame.Surface) -> list[pygame.Surface]:
        shades = []
        for i in range(SHADE_LEVELS):
            factor = MIN_SHADE + (1 - MIN_SHADE) * i / (SHADE_LEVELS - 1)
            shaded = texture.copy()
            gray = int(255 * factor)
            shaded.fill((gray, gray, gray), special_flags=pygame.BLEND_RGB_MULT)
            shades.append(shaded)
        return shades

    def render(self, level: Level, player: Player) -> None:
        hits = self._render_fpp_view(player)
        self._render_minimap(level, player, hits)

    def _render_fpp_view(self, player: Player) -> list[RayHit]:
        width, height = self.screen.get_size()
        half_height = height // 2

        self._render_sky(player.angle, width, half_height)
        self._render_floor(width, height, half_height)

        num_rays = width // STRIP_WIDTH
        hits = self.raycaster.cast_rays_fan(player.center_x, player.center_y, player.angle, FOV, num_rays)

        for i, hit in enumerate(hits):
            x = i * STRIP_WIDTH
            depth = max(hit.depth, MIN_DEPTH)
            proj_height = height / depth
            y = (height - proj_height) / 2

            if self.use_textures:
                self._render_textured_column(x, y, proj_height, hit, depth)
            else:
                color = WALL_COLOR_VERTICAL if hit.is_vertical else WALL_COLOR_HORIZONTAL
                if self.use_shading:
                    color = shaded_color(color, depth)
                pygame.draw.line(self.screen, color, (x, y), (x, y + proj_height), STRIP_WIDTH)

        return hits

    def _render_sky(self, player_angle: float, width: int, half_height: int) -> None:
        img_width = self.sky_texture.get_width()
        offset = int((player_angle / (2 * math.pi)) * img_width) % img_width

        first_width = min(img_width - offset, width)
        self.screen.blit(self.sky_texture, (0, 0), pygame.Rect(offset, 0, first_width, half_height))

        if first_width < width:
            remaining = width - first_width
            self.screen.blit(self.sky_texture, (first_width, 0), pygame.Rect(0, 0, remaining, half_height))

    def _render_textured_column(self, x: int, y: float, proj_height: float, hit: RayHit, depth: float) -> None:
        offset = texture_offset(hit)
        tex_x = min(int(offset * TEXTURE_SIZE), TEXTURE_SIZE - 1)

        if self.use_shading:
            texture = self.shaded_wall_textures[brightness_level_for_depth(depth, hit.is_vertical)]
        else:
            texture = self.wall_texture

        column = texture.subsurface(tex_x, 0, 1, TEXTURE_SIZE)
        column = pygame.transform.scale(column, (STRIP_WIDTH, max(int(proj_height), 1)))
        self.screen.blit(column, (x, y))

    def _render_floor(self, width: int, height: int, half_height: int) -> None:
        if not self.use_shading:
            self.screen.fill(FLOOR_COLOR, pygame.Rect(0, half_height, width, height - half_height))
            return

        for y in range(half_height, height):
            rel_y = max(y - half_height, 1)
            distance = FLOOR_FAKE_PLAYER_Z / (rel_y / height)
            shade = max(MIN_SHADE, 1 - distance * FLOOR_SHADE_FALLOFF)
            color = (int(FLOOR_COLOR[0] * shade), int(FLOOR_COLOR[1] * shade), int(FLOOR_COLOR[2] * shade))
            pygame.draw.line(self.screen, color, (0, y), (width, y))

    def _render_minimap(self, level: Level, player: Player, hits: list[RayHit]) -> None:
        if not self.show_minimap:
            return

        minimap_surface = self.minimap.render(level, player, hits)
        minimap_surface.set_alpha(180)
        position = (8, 8)
        self.screen.blit(minimap_surface, position)
