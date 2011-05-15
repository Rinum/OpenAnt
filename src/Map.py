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
from Ants import *

from random import *
from time import time
#from threading import Timer

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
            self.foliageTiles.append(Tile(self.foliageTilesPath + fname, True))

        self.tiles = numpy.empty([Globals.mapwidth, Globals.mapheight], dtype=object)

        #List of Ants
        self.ants = []
        
        #Active Ant
        self.active = 0
        
        #Waiting for mouse move signal
        Globals.glwidget.mousePress.connect(self.getCoords)
        
        #Double Click?
        self.lastButton = 0
        self.lastClick = 0
        
    def generateMap(self):
        
        self.ants.append(Ants(8, 6, 'worker', 'yellow', 0))  #ants class
        for n in range(Globals.InitialPopulation):
            self.ants.append(Ants(1 + n, 5, 'worker', 'black', n+1))
        
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

    def update(self):
        for ant in self.ants:
            if len(ant.queue):
                ant.queue[0]()

    def getCoords(self, button, x, y):
        '''
        On single click, move ant
        On double click, isse command in context of tile
        '''
        x = (x/Globals.pixelsize)*Globals.pixelsize
        y = (y/Globals.pixelsize)*Globals.pixelsize
        if button == 1:
            # SHOULD: Clear full command queue (gather food, dig, ...)            
            if self.ants[self.active].dig in self.ants[self.active].queue:
                self.ants[self.active].queue.remove(self.ants[self.active].dig) #Cancel previous dig command
            self.ants[self.active].newPos = [x, y]
            self.ants[self.active].queue.append(self.ants[self.active].move)
       
        if self.lastButton == button and time()-self.lastClick < 0.2:
            if self.ants[self.active].dig in self.ants[self.active].queue:
                self.ants[self.active].queue.remove(self.ants[self.active].dig) #Cancel previous dig command
            self.ants[self.active].queue.append(self.ants[self.active].dig)
            self.lastButton = 0 # Quick single click after double click as single click
        else:
            self.lastButton = button           
      
        self.lastClick = time()
        