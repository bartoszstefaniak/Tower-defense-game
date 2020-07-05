"""

This module contains main function which runs game and
chooses suitable window size

"""

import pygame as pg
from statemachine import StateMachine

WINDOW_SIZE = (1280, 768)


def main():
    pg.init()

    window_size = None

    for size in reversed(pg.display.list_modes()):
        if size[0] >= WINDOW_SIZE[0] and size[1] >= WINDOW_SIZE[1]:
            window_size = size
            break

    if window_size is None:
        print("[ERROR] No suitable window size possible")
        return

    print("[INFO] Chosen window size is", window_size)

    screen = pg.display.set_mode(window_size)
    pg.display.set_caption("Gra")
    statemachine = StateMachine(screen)

    statemachine.main_loop()


if __name__ == "__main__":
    main()
