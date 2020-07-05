"""

This module contains class LevelSelectState which is responsible
for drawing level select menu and activating levels

"""

import state
from button import Button


class LevelSelectState(state.State):

    def __init__(self, screen, resource_manager):
        super().__init__("levelselectstate")
        self.resource_manager = resource_manager
        self.screen = screen
        self.textures = resource_manager.textures

        self.BUTTON_SIZE = (160, 55)
        self.BUTTON_SPACING = (200, 50)
        self.button_names = resource_manager.level_data.keys()

        self.buttons = self.create_buttons()

    def update(self, _):
        for i in self.buttons:
            i.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for i in self.buttons:
            i.draw()

    def process_event(self, event):
        for i in self.buttons:
            i.process_event(event)

    def menu(self):
        self.next = "menu"
        self.done = True

    def create_buttons(self):

        self.bttns_in_row = 3
        x, y = 0, -50
        buttons = []
        for idx, name in enumerate(self.button_names):
            if idx % self.bttns_in_row == 0:
                y += self.BUTTON_SPACING[1] + self.BUTTON_SIZE[1]
                x = 225
            tmp = Button(self.screen, self.textures["button"].get_rect(
                           center=self.screen.get_rect().center),
                         [self.textures["button"]],
                         caption=name,
                         command=self.make_select_level(name))

            tmp.rect.y = y

            tmp.rect.x += (((idx % self.bttns_in_row) - 1) *
                           (self.BUTTON_SIZE[0] + self.BUTTON_SPACING[0]))

            buttons.append(tmp)

            x += self.BUTTON_SPACING[0] + self.BUTTON_SIZE[0]

        back_button = Button(self.screen, self.textures["button"].
                             get_rect(center=self.screen.get_rect().
                                      center),
                             [self.textures["button"]],
                             caption="Menu główne", command=self.menu)

        back_button.rect.y += 200

        buttons.append(back_button)

        return buttons

    def make_select_level(self, level_name):
        def select_level():
            self.next_state_args = (level_name, )
            self.done = True
            self.next = "level"
        return select_level
