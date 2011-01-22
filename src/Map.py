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

