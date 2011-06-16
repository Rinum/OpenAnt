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
from WorkerAnt import *

from random import *
from time import time

from const.constants import *

class Tile():
    '''
    Class to represent a tile
    '''
    def __init__(self, image, passable):
        self.image = image
        self.passable = passable

    def __repr__(self):
        return self.image
    
    def isPassable(self):
        return self.passable

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

        #Undeground tiles
        self.undergroundTilesPath = Globals.datadir + 'images/underground/'
        self.undergroundTiles = []
        
        #Populate list of ground tiles
        dirList = os.listdir(self.groundTilesPath)
        for fname in dirList:
            self.groundTiles.append(Tile(self.groundTilesPath + fname, True))

        #Populate list of underground tiles
        dirList = os.listdir(self.undergroundTilesPath)
        for fname in dirList:
            if (fname == "underground1.png"):#underground2.png is for tunnels
                self.undergroundTiles.append(Tile(self.undergroundTilesPath + fname, True))

        #Populate list of foliage tiles
        dirList = os.listdir(self.foliageTilesPath)
        for fname in dirList:
            if "rock" in fname:
                self.foliageTiles.append(Tile(self.foliageTilesPath + fname, False))
            else:
                self.foliageTiles.append(Tile(self.foliageTilesPath + fname, True))

        self.tiles = numpy.empty([Globals.mapwidth, Globals.mapheight], dtype=object)

        #Waiting for mouse move signal
        Globals.glwidget.mousePress.connect(self.getCoords)
        
        #Double Click?
        self.lastButton = 0
        self.lastClick = 0
        
        self.lastX = -1
        self.lastY = -1
        
    def generateMap(self):
        for x in range(Globals.mapwidth):
            for y in range(Globals.mapheight):
                if (y <= Globals.mapheight/2):
                    if randint(0,10) > 8:
                        self.tiles[x][y] = choice(self.foliageTiles)
                    else:
                        self.tiles[x][y] = choice(self.groundTiles)
                else:
                    self.tiles[x][y] = choice(self.undergroundTiles) #underground map

        return View(self.tiles[:,:]) #tiles[every x, every y]

    def spawnAnts(self):
        _x = randint(0, 10)
        _y = randint(0, 10)
        while not self.tiles[_x][_y].isPassable():
            print "Cant spawn on", _x, _y, "because the tile isnt passable."
            _x = randint(0, 10)
            _y = randint(0, 10)
        self.ant = WorkerAnt(_x, _y, self.tiles, Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellowant.png', 2, [32, 32, 32, 32], [_x * 32, _y * 32, 32, 32])) # Ant class
        print self.ant.speed

    def update(self):
        if len(self.ant.queue):
            self.ant.queue[0]()

    def getCoords(self, button, x, y):
        '''
        On click, move ant
        '''
        x = (x/Globals.pixelsize)*Globals.pixelsize
        y = (y/Globals.pixelsize)*Globals.pixelsize
        if button == 1:
            if self.lastButton == button and time()-self.lastClick < 0.5 and x == self.lastX and y == self.lastY:
                if self.ant.dig in self.ant.queue:
                    self.ant.queue.remove(self.ant.dig) #Cancel previous dig command
                self.ant.queue.append(self.ant.dig)
            else:
                # Choose a tile that is passable and next to the tile clicked on.
                while not self.tiles[x/32][y/32].isPassable():
                    if self.ant.pos[0] < x:
                        x -= 32
                    elif self.ant.pos[0] > x:
                        x += 32
                    if self.ant.pos[1] < y:
                        y -= 32
                    elif self.ant.pos[1] > y:
                        y += 32
                self.ant.newPos = [x, y]
                self.ant.queue.append(self.ant.findPath)

        self.lastButton = button
        self.lastClick = time()
        self.lastX = x;
        self.lastY = y;
        
    def getTile(self, x, y):
        return self.tiles[x][y]