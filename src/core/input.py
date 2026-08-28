import pygame


class UserInput:
    def __init__(self, recenter_mouse: bool = False):
        self.quit_requested = False

        self.keys_down = pygame.key.get_pressed()
        self.keys_pressed: set[int] = set()

        self.mouse_pos = (0, 0)
        self.mouse_rel = (0, 0)
        self.mouse_buttons_down = (False, False, False)
        self.mouse_buttons_pressed: set[int] = set()

        self.recenter_mouse = recenter_mouse  # fix for fullscreen - see: _read_mouse_rel
        if self.recenter_mouse:
            self._center = pygame.display.get_surface().get_rect().center
            pygame.mouse.set_pos(self._center)

    def update(self) -> None:
        self.keys_pressed = set()
        self.mouse_buttons_pressed = set()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.quit_requested = True

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    self.quit_requested = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons_pressed.add(event.button)

        self.keys_down = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_buttons_down = pygame.mouse.get_pressed()
        self.mouse_rel = self._read_mouse_rel()

    def _read_mouse_rel(self) -> tuple[int, int]:
        if not self.recenter_mouse:
            # get_rel() causes problems on fullscreen + grab + SCALED ...
            return pygame.mouse.get_rel()

        # ... so in that case it's done manually:
        # diff against the last known center, then snap the cursor back there
        rel = (self.mouse_pos[0] - self._center[0], self.mouse_pos[1] - self._center[1])
        pygame.mouse.set_pos(self._center)
        return rel

    def is_key_down(self, key: int) -> bool:
        return self.keys_down[key]

    def is_key_pressed(self, key: int) -> bool:
        return key in self.keys_pressed

    def is_mouse_down(self, button: int = pygame.BUTTON_LEFT) -> bool:
        # pygame.BUTTON_LEFT/MIDDLE/RIGHT = 1/2/3
        # but get_pressed() returns (left, middle, right) at index 0/1/2
        return self.mouse_buttons_down[button - 1]  # so here is the fix with -1

    def is_mouse_pressed(self, button: int = pygame.BUTTON_LEFT) -> bool:
        return button in self.mouse_buttons_pressed
