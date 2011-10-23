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
from YellowAnt import *
from Food import *

from random import *
from time import time

from threading import Timer

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
            if(fname != "Thumbs.db"):
                self.groundTiles.append(Tile(self.groundTilesPath + fname, True))

        #Populate list of underground tiles
        dirList = os.listdir(self.undergroundTilesPath)
        for fname in dirList:
            if(fname != "Thumbs.db"):
                if (fname == "underground1.png"):#underground2.png is for tunnels
                    self.undergroundTiles.append(Tile(self.undergroundTilesPath + fname, True))

        #Populate list of foliage tiles
        dirList = os.listdir(self.foliageTilesPath)
        for fname in dirList:
            if(fname != "Thumbs.db"):
                if "rock" in fname:
                    self.foliageTiles.append(Tile(self.foliageTilesPath + fname, False))
                else:
                    self.foliageTiles.append(Tile(self.foliageTilesPath + fname, True))

        self.tiles = numpy.empty([Globals.mapwidth, Globals.mapheight * 2], dtype=object)
        Globals.glwidget.mouseMove.connect(self.moveCamera)
        self.occupiedTiles = {}

        #Waiting for mouse move signal
        Globals.glwidget.mousePress.connect(self.getCoords)
        
        #Double Click?
        self.lastButton = 0
        self.lastClick = 0
        
        self.lastX = -1
        self.lastY = -1
        
        # Black colony
        self.blackAnts = []
        # Red colony
        self.redAnts = []
        
        # Food
        self.pos_food = {}

        # Ant Hills
        self.antHills = numpy.zeros([Globals.mapwidth, Globals.mapheight], dtype=int) # [X Coord][Y Coord] = Type (0:Free,1:Ant Hill,2:Nest Entry)
        

    def generateMap(self):
        for x in range(Globals.mapwidth):
            for y in range(Globals.mapheight * 2):
                if (y <= Globals.mapheight):
                    if randint(0,10) > 8:
                        self.tiles[x][y] = choice(self.foliageTiles)
                    else:
                        self.tiles[x][y] = choice(self.groundTiles)
                else:
                    self.tiles[x][y] = choice(self.undergroundTiles) #underground map

        return View(self.tiles[:,:]) #tiles[every x, every y]

    def spawnAnts(self):
        _x, _y = self.getSpawnLocation()
        # Create the ants
        self.yellowAnt = YellowAnt(self,_x, _y, Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellowant.png', 2, [32, 32, 32, 32], [_x * 32, _y * 32, 32, 32]))
        self.occupiedTiles[(_x, _y)] = True

    def getSpawnLocation(self):
        _x = randint(0, 10)
        _y = randint(0, 10)
        while not (self.tiles[_x][_y].isPassable() and not self.occupiedTiles.has_key((_x, _y))):
            _x = randint(0, 10)
            _y = randint(0, 10)
        return _x, _y
    
    def getSpawnLocationDistribution(self, distCenter = (10, 10)):
        '''Used for food spawning, possibly spawning new ants?''' 
        
        stdDev = 2.7

        x, y = numpy.random.normal(distCenter[0], stdDev), numpy.random.normal(distCenter[1], stdDev)
        failCount = 0
        while True:
            failCount += 1
            x, y = numpy.random.normal(distCenter[0], stdDev), numpy.random.normal(distCenter[1], stdDev)
            x, y = int(x), int(y)
            #check if number is even in map/check if passable and not occupied
            if 0 < x < Globals.mapheight and 0 < y < Globals.mapheight:
                if (self.tiles[x][y].isPassable() and not self.occupiedTiles.has_key((x, y))):
                    break
        return x, y

    def spawnOneFood(self, origin = (0, 0), random = False):		
       
        if random:
            x, y = self.getSpawnLocationDistribution(origin)
        else:
            x, y = origin

        self.pos_food[(x, y)] = Food(x, y, Globals.glwidget.createImage(Globals.datadir + 'images/food/food.png', 2, [32, 32, 32, 32], [x * 32, y * 32, 32, 32]))
        self.occupiedTiles[(x, y)] = True
		
    def removeOneFood(self, foodLocation):
        ###remove image, take out of map's food stack, take off of occupiedTiles
        foodParticle = self.pos_food[foodLocation]
        Globals.glwidget.deleteImage(foodParticle.sprite) #delete the image (gfx)
        del self.pos_food[foodLocation] #delete the actual food object
        self.occupiedTiles[foodLocation] = False #unoccupy the position
 
    def update(self):
        if len(self.yellowAnt.queue):
            self.yellowAnt.queue[0]()
        
        #if there are less than 20 pieces of food...
        while len(self.pos_food.keys()) < 50:
            self.spawnOneFood((15, 15), random = True)

    def getCoords(self, button, x, y):
        '''
        On click, move ant.
        '''
        x = (x/Globals.pixelsize)*Globals.pixelsize
        y = (y/Globals.pixelsize)*Globals.pixelsize
        if button == 1:
            if self.lastButton == button and time()-self.lastClick < 0.5 and x == self.lastX and y == self.lastY:
                if self.yellowAnt.doubleClick in self.yellowAnt.queue:
                    self.yellowAnt.queue.remove(self.yellowAnt.doubleClick) #Cancel previous dig command
                self.yellowAnt.queue.append(self.yellowAnt.doubleClick)
            else:
                # Choose a tile that is passable and next to the tile clicked on.
                while not self.tiles[x/32][y/32].isPassable():
                    if self.yellowAnt.pos[0] < x:
                        x -= 32
                    elif self.yellowAnt.pos[0] > x:
                        x += 32
                    if self.yellowAnt.pos[1] < y:
                        y -= 32
                    elif self.yellowAnt.pos[1] > y:
                        y += 32
                self.yellowAnt.newPos = [x, y]
                if self.yellowAnt.moveAlongPath in self.yellowAnt.queue: #User decided to perform a different action sequence
                    print 'remove queue'
                    self.yellowAnt.queue.clear() #Clear queued actions
                    self.yellowAnt.path.clear() #Clear path so ant can move to new location
                self.yellowAnt.queue.append(self.yellowAnt.findPath)

        self.lastButton = button
        self.lastClick = time()
        self.lastX = x;
        self.lastY = y;
        print self.yellowAnt.queue
        print self.yellowAnt.path
        
    def getTile(self, x, y):
        return self.tiles[x][y]
    
    def moveCamera(self,x,y):
        try: # We try and cancel any previous camera movements.
            self.t.cancel()
        except:
            pass

        w = Globals.glwidget.w #viewport width
        h = Globals.glwidget.h #viewport height

        shiftX = 0
        shiftY = 0
        loop = False

        if x<=(0.1*w) and Globals.glwidget.camera[0] + 16 <= Globals.leftBound:
            shiftX = 16
            loop = True
        if x>=(w - 0.1*w) and Globals.glwidget.camera[0] - 16 >= Globals.rightBound +w:
            shiftX = -16
            loop = True
        if y<=(0.1*h) and Globals.glwidget.camera[1] + 16 <= Globals.upBound:
            shiftY = 16
            loop = True
        if y>=(h - 0.1*h) and Globals.glwidget.camera[1] - 16 >= Globals.downBound +h:
            shiftY = -16
            loop = True
     
 
        Globals.glwidget.camera[0] += shiftX
        Globals.glwidget.camera[1] += shiftY

        if loop == True:
            self.t = Timer(0.05, self.moveCamera, (x, y))
            self.t.start()
