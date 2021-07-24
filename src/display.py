import pyglet
from pyglet.window import key
from pyglet.gl import *
import numpy

class DisplayScreen:
    def __init__(self, array, height, length, rescale = True):
        self.screen = array
        self.screen.shape = -1

        self.rescale = rescale
        self.height = height
        self.length = length
        self.format_size = 4
        self.bytes_per_channel = 1
        self.pitch = self.height * self.format_size * self.bytes_per_channel
        self._screenData = (GLubyte * self.screen.size)(*self.screen.astype('uint8'))
        self.image = pyglet.image.ImageData(
            self.length,
            self.height,
            "RGBA",
            self._screenData,
            pitch=self.pitch
        )
        self._update_image()

    def set_screen(self, screen):
        self.screen = screen
        self.screen.shape = -1
        self._screenData = (GLubyte * self.screen.size)(*self.screen.astype('uint8'))

    def _update_image(self):
        self.image.set_data("RGBA", self.pitch, self._screenData)

    def update(self):
        self._update_image()