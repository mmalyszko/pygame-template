from typing import Protocol

import pygame

from src.core.input import UserInput

MAX_DELTA_TIME_MS = 100
FPS_REFRESH_INTERVAL_MS = 1000
FPS_FONT_COLOR_CYAN = (80, 230, 230)


class IGame(Protocol):
    def update(self, dt: float, user_input: UserInput) -> None: ...
    def render(self) -> None: ...


class GameLoop:
    def __init__(self, game: IGame, user_input: UserInput, target_fps: int = 60):
        self.game = game
        self.user_input = user_input
        self.target_fps = target_fps

        self._fps = 0
        self._fps_frame_count = 0
        self._fps_timer = 0.0
        self._fps_font = pygame.font.SysFont(None, 24)

    def start(self) -> None:
        clock = pygame.time.Clock()
        screen = pygame.display.get_surface()

        while True:
            self.user_input.update()
            if self.user_input.quit_requested:
                break

            # pygame docs says: tick() uses SDL_Delay, which "is not accurate on every platform" ...
            # ... so if it happens, tick_busy_loop() does the job better (with some CPU cost)
            dt = min(clock.tick_busy_loop(self.target_fps), MAX_DELTA_TIME_MS)
            self._update_fps_counter(dt)

            self.game.update(dt, self.user_input)
            self.game.render()

            self._render_fps_counter(screen)

            pygame.display.flip()

    def _update_fps_counter(self, dt: float) -> None:
        self._fps_frame_count += 1
        self._fps_timer += dt
        if self._fps_timer >= FPS_REFRESH_INTERVAL_MS:
            self._fps = self._fps_frame_count
            self._fps_frame_count = 0
            self._fps_timer = 0.0

    def _render_fps_counter(self, screen: pygame.Surface) -> None:
        fps_text = self._fps_font.render(f"FPS: {self._fps}", True, FPS_FONT_COLOR_CYAN)
        screen.blit(fps_text, fps_text.get_rect(topright=(screen.get_width() - 10, 10)))
