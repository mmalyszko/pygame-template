import math

import pygame

from src.core.input import UserInput
from src.core.objects import GameObject
from src.game.level import Level

PLAYER_RADIUS = 0.32
PLAYER_SPEED = 0.004

MOUSE_SENSITIVITY = 0.0025
MOUSE_MAX_REL = 40


class Player(GameObject):
    def __init__(self, center_x: float, center_y: float):
        super().__init__(center_x, center_y)
        self.radius = PLAYER_RADIUS
        self.angle = 0.0

    def look(self, user_input: UserInput) -> None:
        mouse_dx, _ = user_input.mouse_rel
        mouse_dx = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, mouse_dx))  # clamps mouse spikes
        self.angle = (self.angle + mouse_dx * MOUSE_SENSITIVITY) % (2 * math.pi)

    def move(self, dt: float, user_input: UserInput, level: Level) -> None:
        forward = 0
        strafe = 0

        if user_input.is_key_down(pygame.K_UP) or user_input.is_key_down(pygame.K_w):
            forward += 1
        if user_input.is_key_down(pygame.K_DOWN) or user_input.is_key_down(pygame.K_s):
            forward -= 1
        if user_input.is_key_down(pygame.K_RIGHT) or user_input.is_key_down(pygame.K_d):
            strafe += 1
        if user_input.is_key_down(pygame.K_LEFT) or user_input.is_key_down(pygame.K_a):
            strafe -= 1

        # fixes too-fast movement when two keys are held at once (e.g. W+D)
        forward, strafe = self._normalize(forward, strafe)

        forward_x, forward_y = math.cos(self.angle), math.sin(self.angle)
        strafe_x, strafe_y = -forward_y, forward_x

        dx = (forward * forward_x + strafe * strafe_x) * PLAYER_SPEED * dt
        dy = (forward * forward_y + strafe * strafe_y) * PLAYER_SPEED * dt

        next_x = self.center_x + dx
        if level.can_move_to(next_x, self.center_y, self.radius):
            self.center_x = next_x

        next_y = self.center_y + dy
        if level.can_move_to(self.center_x, next_y, self.radius):
            self.center_y = next_y

    def _normalize(self, forward: float, strafe: float) -> tuple[float, float]:
        magnitude = math.hypot(forward, strafe)
        if magnitude == 0:
            return forward, strafe
        return forward / magnitude, strafe / magnitude
