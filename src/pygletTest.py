import pyglet
from pyglet.window import key
from pyglet.gl import *
import numpy

from display import DisplayScreen

NES_RES_LENGTH = 256
NES_RES_HIGHT = 240
window = pyglet.window.Window(640, 480)

label = pyglet.text.Label('Hello',
                          font_name='Times New Roman',
                          font_size=32,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

image = pyglet.resource.image('kitten.png')
data = numpy.random.randint(
    low=0,
    high=255,
    size = (NES_RES_HIGHT*NES_RES_LENGTH,4)
)

screen = DisplayScreen(data, NES_RES_HIGHT, NES_RES_LENGTH)

glScalef(2.0, 2.0, 2.0)

def updateData(data, screen):
    data += 30
    screen.set_screen(data)
    screen.update()    
    pass

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.SPACE:
        updateData(data, screen)
        
    #print(symbol)


@window.event
def on_draw():
    window.clear()
    #The following two lines will change how textures are scaled.
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    #image.blit(0,0)
    screen.image.blit(0,0)
    #label.draw()

pyglet.app.run()
