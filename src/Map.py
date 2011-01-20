import Globals
from GLWidget import *

class Map():
    def __init__(self):
        for y in xrange(0, Globals.mapheight, 1):
            for x in xrange(0, Globals.mapwidth, 1):
               Globals.glwidget.createImage(Globals.datadir + "images/tile-dirt.png", 3, [0, 0, -1, -1], [(Globals.pixelsize*x)-((Globals.mapwidth/2)*Globals.pixelsize), (Globals.pixelsize*y)-((Globals.mapheight/2)*Globals.pixelsize), Globals.pixelsize, Globals.pixelsize])
