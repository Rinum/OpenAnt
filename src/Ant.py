# -*- coding: utf-8 -*-
#
# This file is part of Open Ant.
#
# Open Ant is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Open Ant is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Open Ant.  If not, see <http://www.gnu.org/licenses/>.
#
# Ant class

from GLWidget import *
from PyQt4.QtCore import *

from algo.astar import *
import collections
from random import *

class Ant():
    '''
    Class for generating ants
    '''

    def __init__(self, parent, xpos, ypos, sprite):
        # Current position.
        self.pos = [xpos * 32, ypos * 32]
        # A path to go from self.pos to self.newPos using A*.
        self.path = collections.deque()
        # The end of the path.
        self.newPos = [xpos * 32, ypos * 32]
        # The next node in the path to move to.
        self.nextPos = [-1, -1]
        
        self.N = [0, 32, 32, 32]
        self.S = [32, 32, 32, 32]
        self.E = [64, 32, 32, 32]
        self.W = [96, 32, 32, 32]
        self.NW = [0, 0, 32, 32]
        self.NE = [32, 0, 32, 32]
        self.SW = [64, 0, 32, 32]
        self.SE = [96, 0, 32, 32]
        self.sprite = sprite
        self.sprite.setTextureRect(self.S)
        self.direction = self.S
        self.queue = collections.deque()
        
        self.speed = 4
        
        self.parent = parent
        
        self.moving = False
        self.hasFood = False
 
    def setSprite(self, sprite):
        self.sprite = sprite
        
    def switchSprite(self, imgLocation):
        '''Not sure if I should use the setSprite Command above'''
        
        #delete previous sprite/add new one
        Globals.glwidget.deleteImage(self.sprite)
        self.sprite = Globals.glwidget.createImage(imgLocation, 2, [32, 32, 32, 32], [self.pos[0], self.pos[1], 32, 32])

    def move(self):
        if len(self.path) or self.pos != self.nextPos:
            if self.moving:
                newDirection = ""
                if self.pos[0] < self.nextPos[0]:
                    # The following line makes it so that your speed does not need to be a factor of 32 (or whatever the tile size is).
                    if self.nextPos[0] - self.pos[0] < self.speed:
                        self.pos[0] += self.nextPos[0] - self.pos[0]
                    else:
                        self.pos[0] += self.speed
                    newDirection = "E"
                elif self.pos[0] > self.nextPos[0]:
                    if self.pos[0] - self.nextPos[0] < self.speed:
                        self.pos[0] -= self.pos[0] - self.nextPos[0]
                    else:
                        self.pos[0] -= self.speed
                    newDirection = "W"
                if self.pos[1] < self.nextPos[1]:
                    if self.nextPos[1] - self.pos[1] < self.speed:
                        self.pos[1] += self.nextPos[1] - self.pos[1]
                    else:
                        self.pos[1] += self.speed
                    newDirection = "S" + newDirection
                elif self.pos[1] > self.nextPos[1]:
                    if self.pos[1] - self.nextPos[1] < self.speed:
                        self.pos[1] -= self.pos[1] - self.nextPos[1]
                    else:
                        self.pos[1] -= self.speed
                    newDirection = "N" + newDirection
                
                # Update sprite.
                if newDirection != "":
                    newDirection = "self." + newDirection
                    self.direction = eval(newDirection)
                    self.sprite.setTextureRect(self.direction) # Update sprite direction.
                    
                if self.pos == self.nextPos:
                    self.moving = False
            else:
                _pos = self.path.popleft()
                self.nextPos[0] = _pos[0] * 32
                self.nextPos[1] = _pos[1] * 32
                self.moving = True
        else:
            self.queue.popleft() #Ant has reached its destination.
        
        self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])

    def dig(self):
        #check if Ant Hill can be built
        diggable = 1
        for i in range(-2,3):
                for j in range(-2,3):
                    if(self.parent.antHills[(self.pos[0]/32)+i][(self.pos[1]/32)+j] > 0):
                        diggable = 0
    
        if(diggable):
            print "We Can Dig!"
            x = self.pos[0] - 32
            y = self.pos[1] - 32
            Globals.glwidget.createImage(Globals.datadir + 'images/special/nest.png', 1, [1, 1, -1, -1], [ x, y, 96, 96]);
            #Prevent overlapping anthills
            for i in range(-2,3):
                for j in range(-2,3):
                    self.parent.antHills[(self.pos[0]/32)+i][(self.pos[1]/32)+j] = 1;
            #Actual Entrance
            self.parent.antHills[self.pos[0]/32][self.pos[1]/32] = 2;
        else:
            print "You Can't Dig There!"
        self.queue.popleft()

    def enterNest(self):
        print "Enter Nest"
        Globals.glwidget.camera[0] = Globals.blackNestX
        Globals.glwidget.camera[1] = Globals.blackNestY
        Globals.upBound = Globals.blackNestY
        Globals.downBound *= 2
        Globals.leftBound = Globals.blackNestX
        Globals.rightBound = Globals.redNestX
        
        self.direction = self.S
        self.sprite.setTextureRect(self.direction) # Update sprite direction.
        self.pos[0] = Globals.blackNestX
        self.pos[1] = Globals.blackNestY
        self.sprite.setDrawRect([self.pos[0] * -1, self.pos[1] * -1, 32, 32])
        
        self.queue.popleft()
        
    def posToTileCoords(self):
        return (self.pos[0]/32, self.pos[1]/32)

    def pickFoodUp(self, antLocationTile):
        self.parent.removeOneFood(antLocationTile)
        self.switchSprite(Globals.datadir + 'images/ants/yellowant_food.png')
        self.sprite.setTextureRect(self.direction)
        self.hasFood = True
        self.queue.popleft() #I hope this is right...

    def setFoodDown(self, antLocationTile):
        self.parent.spawnOneFood(antLocationTile)
        self.switchSprite(Globals.datadir + 'images/ants/yellowant.png')
        self.sprite.setTextureRect(self.direction)
        self.hasFood = False
        self.queue.popleft() 
    
    def doubleClick(self):

        antLocationTile = self.posToTileCoords()
        
        #User probably wants to pick up food
        if (not self.hasFood) and (antLocationTile in self.parent.pos_food):
            print 'Pick up food'
            self.pickFoodUp(antLocationTile)
        
        #User probably wants to set food down (not over nest entrance/other food)
        elif self.hasFood and self.parent.antHills[(self.pos[0]/32)][(self.pos[1]/32)] != 2:
            if antLocationTile in self.parent.pos_food:
                print 'No setting food on top of other food'
                self.queue.popleft()
            else:                
                print 'Set down food'
                self.setFoodDown(antLocationTile)

        #User probably wants to enter the nest
        elif(self.parent.antHills[(self.pos[0]/32)][(self.pos[1]/32)] == 2):
            print 'Enter Nest'
            self.enterNest()

        #User probably wants to dig
        elif(self.parent.antHills[(self.pos[0]/32)][(self.pos[1]/32)] == 0):
            print 'Dig Nest'
            self.dig()
        
        #Who knows what the user wants to do? But we have to clear the queue event.
        else:            
            print 'Dbl clicking here does not do anything...'
            self.queue.popleft()

    # Find a path using A* Manhattan
    def findPath(self):
        start = [self.pos[0] / 32, self.pos[1] / 32]
        end = [self.newPos[0] / 32, self.newPos[1] / 32]
        
        # Start and end are the same tile, dont need to move.
        if start == end:
            self.queue.popleft()
            return
        
        map = self.getMap(start, end)
        
        a = AStar(map, MANHATTAN)
        q = collections.deque()
        
        a.step(q)

        for elem in a.path:
            self.path.append(elem)
        
        if not len(self.path):
            self.queue.popleft()
            return
        
        self.path.popleft()
        
        self.queue.popleft()
        self.queue.append(self.move)
    
    def findAltPath(self, avoid):
        start = [self.pos[0] / 32, self.pos[1] / 32]
        end = [self.newPos[0] / 32, self.newPos[1] / 32]
        # Start and end are the same tile, dont need to move.
        if start == end:
            self.queue.popleft()
            return
        
        map = self.getMap(start, end, avoid)
        
        a = AStar(map, MANHATTAN)
        q = collections.deque()
        
        a.step(q)
        
        self.path.clear()
        for elem in a.path:
            self.path.append(elem)
        
        if not len(self.path):
            self.queue.popleft()
            return
        
        self.path.popleft()
        
    def getMap(self, start, end, avoid = None):
        """Generate a string representation of the map."""
        output = ""

        for i in range(Globals.mapheight):
            for j in range(Globals.mapwidth):
                if avoid is None:
                    if start[0] == j and start[1] == i:
                        output += SOURCE
                    elif end[0] == j and end[1] == i:
                        output += TARGET
                    elif self.parent.tiles[j][i].isPassable():
                        output += NORMAL
                    else:
                        output += BLOCKED
                else:
                    if start[0] == j and start[1] == i:
                        output += SOURCE
                    elif end[0] == j and end[1] == i:
                        output += TARGET
                    elif self.parent.occupiedTiles.has_key((j,i)):
                        output += BLOCKED
                    elif self.parent.tiles[j][i].isPassable():
                        output += NORMAL
                    else:
                        output += BLOCKED
            output += "\n"
        return output
