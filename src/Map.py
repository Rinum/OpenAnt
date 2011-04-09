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
        self.ant = Ants(8, 6) #ants class
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

        #Waiting for mouse move signal
        #Globals.glwidget.mouseMove.connect(self.moveCamera)
        Globals.glwidget.mousePress.connect(self.getCoords)
        
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


    def update(self):
        if self.ant.pos != self.ant.newPos:
            #Globals.view.blackNest()
            self.ant.move(self.ant.newPos[0]/Globals.pixelsize, self.ant.newPos[1]/Globals.pixelsize)

    def move2Camera(self,x,y,speed = 3):
        try: # We try and cancel any previous camera movements.
            self.t.cancel()
        except:
            pass
	
        w = Globals.glwidget.w #viewport width
        h = Globals.glwidget.h #viewport height

        mousePosX = x
        mousePosY = y
        loop = False

        if x<=(0.1*w) and Globals.glwidget.camera[0]<=Globals.leftBound:
            mousePosX += 1 * speed
            loop = True
        if x>=(w - 0.1*w) and Globals.glwidget.camera[0]>=Globals.rightBound +w:
            mousePosX -= 1 * speed
            loop = True
        if y<=(0.1*h) and Globals.glwidget.camera[1]<=Globals.upBound:
            mousePosY += 1 * speed
            loop = True
        if y>=(h - 0.1*h) and Globals.glwidget.camera[1]>=Globals.downBound +h:
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
