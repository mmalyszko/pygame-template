from enum import Enum, auto

import pygame

from src.core.input import UserInput
from src.core.raycasting import Raycaster
from src.game.level import Level
from src.game.objects import Player
from src.game.renderer import Renderer


class GameState(Enum):
    LOADING = auto()
    PLAYING = auto()


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = GameState.LOADING

        self._loading_screen_rendered = False
        self._loading_font = pygame.font.SysFont(None, 48)

        self.level = Level()
        self.raycaster = Raycaster(self.level)
        self.renderer = Renderer(self.screen, self.raycaster)

        spawn_x, spawn_y = self.level.spawn_position()
        self.player = Player(spawn_x, spawn_y)

    def update(self, dt: float, user_input: UserInput) -> None:
        if self.state == GameState.LOADING:
            self._process_loading_state()
            return

        self.player.look(user_input)
        self.player.move(dt, user_input, self.level)

        if user_input.is_key_pressed(pygame.K_0):
            self.renderer.use_shading = not self.renderer.use_shading

        if user_input.is_key_pressed(pygame.K_9):
            self.renderer.use_textures = not self.renderer.use_textures

        if user_input.is_key_pressed(pygame.K_m):
            self.renderer.show_minimap = not self.renderer.show_minimap

    def _process_loading_state(self) -> None:
        if self._loading_screen_rendered:
            self.renderer.load_resources()
            self.state = GameState.PLAYING
        else:
            self._loading_screen_rendered = True

    def render(self) -> None:
        if self.state == GameState.LOADING:
            self.screen.fill((20, 20, 30))
            text = self._loading_font.render("Loading...", True, (230, 230, 230))
            self.screen.blit(text, text.get_rect(center=self.screen.get_rect().center))
            return

        self.renderer.render(self.level, self.player)
