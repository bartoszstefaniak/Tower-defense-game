"""

This module contains class State which is base class for
all states in game

"""


class State:
    """


    """

    def __init__(self, name):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
        self.next_state_args = tuple()
        self.name = name

    def update(self, dt):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()

    def cleanup(self):
        pass

    def process_event(self, event):
        pass

    def startup(self, *args):
        pass
