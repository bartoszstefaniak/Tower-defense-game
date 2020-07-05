"""

This module contains class MenuState which is resposible for drawing main menu,
interacting with player.

"""


from state import State
from button import Button


class MenuState(State):

    def __init__(self, screen, resource_manager):
        super().__init__("menu")

        self.resource_manager = resource_manager
        self.textures = resource_manager.scaled_textures
        self.screen = screen
        self.buttons = self.create_buttons()

    def update(self, dt):
        for button in self.buttons:
            button.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for button in self.buttons:
            button.draw()

    def startup(self, screen, *args):
        self.screen = screen
        self.textures = self.resource_manager.scaled_textures

        self.buttons = self.create_buttons()

    def process_event(self, event):
        for i in self.buttons:
            i.process_event(event)

    def go_to_level_select(self):
        self.done = True
        self.next = "levelselect"

    def go_to_level(self):
        self.next_state_args = ("level1", False)
        self.done = True
        self.next = "level"

    def exit_game(self):
        self.done = True
        self.quit = True

    def create_buttons(self):
        buttons = []

        continue_button = Button(self.screen, self.textures["button"].get_rect(
                       center=self.screen.get_rect().center),
                                         [self.textures["button"]],
                                         caption="Kontynuuj",
                                         command=self.go_to_level)
        continue_button.rect.y -= 200

        buttons.append(continue_button)

        level_select = Button(self.screen, self.textures["button"].get_rect(
                       center=self.screen.get_rect().center),
                                         [self.textures["button"]],
                                         caption="Wybór poziomu",
                                         command=self.go_to_level_select)
        buttons.append(level_select)

        exit_button = Button(self.screen, self.textures["button"].get_rect(
                             center=self.screen.get_rect().center),
                             [self.textures["button"]],
                             caption="Wyjdź",
                             command=self.exit_game)

        exit_button.rect.y += 200

        buttons.append(exit_button)

        return buttons
