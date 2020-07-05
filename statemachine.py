"""

This module contains class StateMachine which is resposible for managing
states and running game

"""

import pygame as pg
import resourcemanager
from menustate import MenuState
from levelselectstate import LevelSelectState
from levelstate import LevelState
from pygame.surface import Surface


class StateMachine:
    SCREEN_SIZE = (1280, 768)
    FPS = 144

    def __init__(self, screen):
        self.quit = False
        self.done = False
        self.screen = screen
        self.clock = pg.time.Clock()
        self.next_lvl = "level1"

        self.resource_manager = resourcemanager.ResourceManager()

        self.states = {"menu": MenuState(Surface(
                                         StateMachine.SCREEN_SIZE),
                                         self.resource_manager),

                       "levelselect": LevelSelectState(Surface(
                                         StateMachine.SCREEN_SIZE),
                                         self.resource_manager),

                       "level": LevelState(Surface(
                                    StateMachine.SCREEN_SIZE),
                                    self.resource_manager),
                       }

        self.state = self.states["menu"]

    def change_state(self):
        self.state.done = False

        if self.state.next is None:
            self.quit = True
            return

        self.states[self.state.next].startup(Surface(StateMachine.SCREEN_SIZE),
                                             *self.state.next_state_args)

        self.state = self.states[self.state.next]

    def update(self, dt):
        if self.state.quit:
            self.quit = True
        elif self.state.done:
            self.change_state()
        else:
            self.state.update(dt)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

            self.state.process_event(event)

    def main_loop(self):
        while not self.quit:
            self.screen.fill((0, 0, 0))
            delta_time = self.clock.tick(StateMachine.FPS)/1000.0

            self.event_loop()
            self.update(delta_time)

            self.state.draw()
            self.screen.blit(self.state.screen, (0, 0))

            if self.state.quit:
                self.quit = True

            pg.display.update()
            self.clock.tick(StateMachine.FPS)
