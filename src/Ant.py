import Globals
import time
from GLWidget import *
from PyQt4.QtCore import *

class Ant():
    posX = 0
    posY = 0
    sprite = None
    def __init__(self):
        self.sprite = Globals.glwidget.createImage(Globals.datadir + "images/ant-player.png", 4, [0, 0, -1, -1], [0, 0, Globals.pixelsize, Globals.pixelsize])
	Globals.glwidget.mousePress.connect(self.getCoords)

    def move(self, x, y):
	while (self.posX != x) and (self.posY != y):
            if self.posX < x:
                self.posX += 1 
            elif self.posX > x:
                self.posX -= 1 
            if self.posY < y:
                self.posY += 1 
            elif self.posY > y:
                self.posY -= 1
	    self.sprite.setDrawRect([x, y, Globals.pixelsize, Globals.pixelsize])
	    time.sleep(1)

    def getCoords(self, button, x, y):
	if(button == -1):
	    self.move(x, y)
