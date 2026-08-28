import pygame

from src.core.input import UserInput
from src.core.loop import GameLoop
from src.game.game import Game

# --- SCREEN CONFIG ---
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WINDOW_TITLE = "Pygame Template"
IS_FULLSCREEN = False
SHOW_CURSOR = False
RECENTER_MOUSE = True  # fix for FPP games (see: UserInput._read_mouse_rel)


def main() -> None:
    pygame.init()

    flags = pygame.SCALED | (pygame.FULLSCREEN if IS_FULLSCREEN else 0)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    pygame.display.set_caption(WINDOW_TITLE)

    if not SHOW_CURSOR:
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    user_input = UserInput(RECENTER_MOUSE)
    game = Game(screen)

    loop = GameLoop(game, user_input)
    loop.start()

    pygame.quit()


if __name__ == "__main__":
    main()
