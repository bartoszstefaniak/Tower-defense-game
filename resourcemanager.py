"""

This module contains class ResourceManager which is resposible for
reading game date from files and storing information

"""

import json
from pygame import image as img


class ResourceManager:
    """

    """

    def __init__(self):

        self.level_data = self.load_data("resources/level_data.json")
        self.textures = self.load_textures("resources/texture_data.json")
        self.maps = self.load_data("resources/maps.json")
        self.scaled_textures = self.textures.copy()

    def load_data(self, path):
        data = None
        with open(path, "r") as json_file:
            data = json.load(json_file)
        return data

    def load_textures(self, path):
        texture_data = None
        with open(path, "r") as json_file:
            texture_data = json.load(json_file)

        textures = {}

        for name in texture_data:
            textures[name] = img.load("resources/textures/" +
                                      name + ".png").convert_alpha()

        return textures
