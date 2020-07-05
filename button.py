"""

This module contains class Button which is responsible
for creating, drawing, using buttons.

"""

import pygame as pg


class Button:
    """

    """

    def __init__(self, screen, rect, texture=None, caption="",
                 fg_color=(255, 255, 255, 0), bg_color=(0, 0, 0, 0),
                 command=lambda: 0, args=[], split=True):

        # 3 różne stany przycisków
        if texture is not None and len(texture) == 1:
            texture = 3 * texture

        self.button_surface = pg.surface.Surface((rect.width, rect.height),
                                                 pg.SRCALPHA, 32)

        self.screen = screen

        self.bg_color = bg_color
        self.fg_color = fg_color
        self.texture = texture
        self.rect = rect
        self.on = False
        self.clicked = False
        self.active = True
        self.caption = caption

        self.BASICFONT = pg.font.Font("resources/arial.ttf", 20)

        self.text_surface = self.BASICFONT.render(caption, True, fg_color)
        self.text_rect = self.text_surface.get_rect(center=(rect.width/2,
                                                    rect.height/2))
        self.command = command
        self.screen = screen
        self.args = args

    def draw(self):
        self.screen.blit(self.button_surface, self.rect)

    def update(self):
        self.button_surface.fill(self.bg_color)

        mouse_position = pg.mouse.get_pos()

        if self.texture is not None:
            if self.on:
                self.button_surface.blit(self.texture[0], (0, 0))
            else:
                if self.rect.collidepoint(mouse_position):
                    self.button_surface.blit(self.texture[1], (0, 0))
                else:
                    self.button_surface.blit(self.texture[2], (0, 0))
        if self.caption is not None:
            self.button_surface.blit(self.text_surface, self.text_rect)

    def process_event(self, event):
        if self.active is True:
            if event.type == pg.MOUSEBUTTONUP:
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    self.on ^= 1
                    self.command(*self.args)

            if event.type == pg.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(pg.mouse.get_pos()):
                    self.clicked = 1

    def toggle_active(self):
        self.active ^= 1

    def set_command(self, command, *args):
        self.command = command
        self.args = args
