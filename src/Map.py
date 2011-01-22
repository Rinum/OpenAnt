# -*- coding: utf-8 -*-
#
# This file is part of Open Ant.
#
# Open Ant is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Open Ant.  If not, see <http://www.gnu.org/licenses/>.
#
# Map Class

import os

import Globals
import numpy
from View import View

from random import *
from threading import Timer

class Tile():
    '''
    Class to represent a tile
    '''
    def __init__(self, image, passable):
        self.image = image
        self.passable = passable

    def __repr__(self):
        return self.image

class Map():
    '''
    Class for generating maps
    '''
    def __init__(self):
        #Ground tiles
        self.groundTilesPath = Globals.datadir + 'images/ground/'
        self.groundTiles = []

        #Foliage tiles
        self.foliageTilesPath = Globals.datadir + 'images/foliage/'
        self.foliageTiles = []

        #Populate list of ground tiles
        dirList = os.listdir(self.groundTilesPath)
        for fname in dirList:
            self.groundTiles.append(Tile(self.groundTilesPath + fname, True))

        #Populate list of foliage tiles
        dirList = os.listdir(self.foliageTilesPath)
        for fname in dirList:
            self.foliageTiles.append(Tile(self.foliageTilesPath + fname, False))

	    self.dirtTile = Tile(Globals.datadir + 'images/tile-dirt.png', True)

        self.tiles = numpy.empty([Globals.mapwidth, Globals.mapheight, Globals.mapdepth], dtype=object)

        #Waiting for mouse move signal
        Globals.glwidget.mouseMove.connect(self.moveCamera)
        
    def generateMap(self):
        for x in range(Globals.mapwidth):
            for y in range(Globals.mapheight):
                if randint(0,10) > 8:
                    self.tiles[x][y][0] = choice(self.foliageTiles)
                else:
                    self.tiles[x][y][0] = choice(self.groundTiles)
                for z in range(1, Globals.mapdepth):
                    self.tiles[x][y][z] = self.dirtTile
        self.groundView = View(self.tiles[:,:,0]) #tiles[every x, every y, only 0 for z]
        # Uncomment the next line (and comment the above line) for underground view.
        #self.undergroundView = View(self.tiles[:,0,:]) #tiles[every x, only 0 for y, every z]

    def moveCamera(self,x,y):
        try: # We try and cancel any previous camera movements.
	    self.t.cancel()
	except:
	    pass
	
        w = Globals.glwidget.w #viewport width
        h = Globals.glwidget.h #viewport height

        mousePosX = x
        mousePosY = y

        if x<=(0.1*w):
            mousePosX += 1
        if x>=(w - 0.1*w):
            mousePosX -= 1
        if y<=(0.1*h):
            mousePosY += 1
        if y>=(h - 0.1*h):
            mousePosY -= 1
        Globals.glwidget.camera[0] += mousePosX - x
        Globals.glwidget.camera[1] += mousePosY - y

        if ((x<=(0.1*w)) or (x>=(w - 0.1*w)) or (y<=(0.1*h)) or (y>=(h - 0.1*h))):
            self.t = Timer(0.01, self.moveCamera, (x, y))
            self.t.start()
