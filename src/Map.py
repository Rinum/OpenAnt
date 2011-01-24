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
        self.ant = Ants(8, 6) #ants class
        self.ant2 = Ants(0, 0)
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
        Globals.glwidget.mousePress.connect(self.getCoords)
        
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
        self.undergroundView = View(self.tiles[:,0,:], True) #tiles[every x, only 0 for y, every z]
        self.view = self.groundView

    def update(self):
        if self.ant.pos != self.ant.newPos:
            self.ant.move(self.ant.newPos[0]/24, self.ant.newPos[1]/24)
            self.view.setView(self.undergroundView)
        if self.ant2.moving == False:
            self.ant2.newPos = [randint(0, Globals.mapwidth)*24, randint(0, Globals.mapheight)*24]
            self.ant2.moving = True
	    print self.ant2.newPos[0], self.ant2.newPos[1]
        if self.ant2.pos != self.ant2.newPos:
            self.ant2.move(self.ant2.newPos[0]/24, self.ant2.newPos[1]/24)
        else:
            self.ant2.moving = False

    def moveCamera(self,x,y,speed = 2):
        try: # We try and cancel any previous camera movements.
	    self.t.cancel()
	except:
	    pass
	
        w = Globals.glwidget.w #viewport width
        h = Globals.glwidget.h #viewport height

        mousePosX = x
        mousePosY = y
        loop = False

        if x<=(0.1*w) and Globals.glwidget.camera[0]<=0:
            mousePosX += 1 * speed
            loop = True
        if x>=(w - 0.1*w) and Globals.glwidget.camera[0]>=Globals.mapwidth*-24 +w:
            mousePosX -= 1 * speed
            loop = True
        if y<=(0.1*h) and Globals.glwidget.camera[1]<=0:
            mousePosY += 1 * speed
            loop = True
        if y>=(h - 0.1*h) and Globals.glwidget.camera[1]>=Globals.mapheight*-24 +h:
            mousePosY -= 1 * speed
            loop = True
        Globals.glwidget.camera[0] += mousePosX - x
        Globals.glwidget.camera[1] += mousePosY - y

        if loop == True:
            self.t = Timer(0.01, self.moveCamera, (x, y))
            self.t.start()

    def getCoords(self, button, x, y):
        '''
        On click, move ant
        '''
	if button == 1:
            self.ant.newPos = [x, y]
