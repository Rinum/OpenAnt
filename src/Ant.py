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
import math

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
        self.underground = False
        
        self.speed = 4
        
        self.parent = parent
        
        self.moving = False
        self.hasFood = False
 
    def switchSprite(self, imgLocation):
        '''Not sure if I should use the setSprite Command above'''
        
        if imgLocation != self.sprite.imagepath:
            #delete previous sprite/add new one
            Globals.glwidget.deleteImage(self.sprite)
            self.sprite = Globals.glwidget.createImage(imgLocation, 2, self.direction, [self.pos[0], self.pos[1], 32, 32])
        else:
            #update sprite with new position
            self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])

    def traverseLineSeqment(self, distanceToTravel):
        '''Used to easily calculate new positions and positional overflow
        Might not be efficient ant by ant, but if we put all ant positions in an array
        and then calculate it will be fast.  For now I used math instead of numpy
        because it is faster when not using arrays.  Doing it this way also allows an easy
        transition to absolute (non-tile) movement if we want to change it.
        ---> (newPosition, overflow)'''

        #nifty arctan that takes quadrant into consideration (goes y then x)
        rads = math.atan2(self.nextPos[1] - self.pos[1], self.nextPos[0] - self.pos[0])

        #proportion of the distance we apply to each axis, takes into account (-) rad values
        _xProportion = math.cos(rads)
        _yProportion = math.sin(rads)

        newPosition = ( self.pos[0] + _xProportion*distanceToTravel, #new x pos 
                        self.pos[1] + _yProportion*distanceToTravel) #new y pos 

        #check if you moved past self.nextPos and report the amount, set newPos to self.nextPos if true. 
        movedDistance = math.sqrt( (newPosition[0] - self.pos[0])**2 + (newPosition[1] - self.pos[1])**2 )
        distanceToPathEnd = math.sqrt( (self.nextPos[0] - self.pos[0])**2 + (self.nextPos[1] - self.pos[1])**2 )

        if movedDistance > distanceToPathEnd: 
            _distanceOverflow = movedDistance - distanceToPathEnd 
            return (self.nextPos, _distanceOverflow)
        else:
            return (newPosition, 0)

    def updateDirection(self):
        '''--> True or False (whether direction changed)'''
        
        #we aren't heading anywhere, retain current direction
        if self.pos == self.nextPos:
            return False
        
        #if we are going somewhere
        newDirection = ''
        if self.pos[0] < self.nextPos[0]:
            newDirection = "E"
        elif self.pos[0] > self.nextPos[0]:
            newDirection = "W"
        if self.pos[1] < self.nextPos[1]:
            newDirection = "S" + newDirection
        elif self.pos[1] > self.nextPos[1]:
            newDirection = "N" + newDirection
        
        newDirection = "self." + newDirection
        newDirection = eval(newDirection)
        if self.direction == newDirection:
            return False
        else:
            self.direction = newDirection
            return True


    def moveAlongPath(self):
        '''Attempts to take care of stuttering
        - Only pops path once destination is reached, that way path ALWAYS represents where we are going
        - Moves until ALL distance is depleted, not just if next tile if reached'''

        #if this is first move call in series(don't pop!)
        if not self.moving:
            self.moving = True
            self.nextPos = self.path[0]
            self.nextPos = self.nextPos[0] * 32, self.nextPos[1] * 32

        #update position till distance depletes
        directionChanged = False
        distanceLeft = self.speed
        while len(self.path) and distanceLeft:
            '''move position until you run out of distance'''
            directionChanged = self.updateDirection() #must be before pos change.!!!exec every loop?
            self.pos, distanceLeft = self.traverseLineSeqment(distanceLeft)    
            
            #update next position if we aren't there yet
            if self.pos == self.nextPos: 
                self.path.popleft()
                if len(self.path):
                    self.nextPos = self.path[0]
                    self.nextPos = self.nextPos[0] * 32, self.nextPos[1] * 32
        
        #Update Sprite (position and direction) 
        if directionChanged: self.sprite.setTextureRect(self.direction) 
        self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])
        
        #check if done moving (reached ultimate destination, not just next tile)
        if not self.path:
            self.queue.popleft()
            self.moving = False
            
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


    def lerpMoveSimple(self, interTime):
        '''just move using direction/speed
        - no moving past next tile/change direction'''

        distanceToTravel = self.speed * interTime

        #traverse makes no state changes
        newPos, overDistance = self.traverseLineSeqment(distanceToTravel) 
        self.sprite.setDrawRect([newPos[0], newPos[1], 32, 32])

    def lerpMove(self, interTime):
        '''Differs from simple in that it will go to next tile. Change Direction'''
        
        #speed is pixels/logic loop
        amount = interTime*self.speed

        #problem with this is it updates position...
        #self.moveAlongPath()
        #need to make lerpAlongPath that doesn't update...

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
        print "Enter Nest2"
        Globals.glwidget.camera[0] = Globals.blackNestX
        Globals.glwidget.camera[1] = Globals.blackNestY
        Globals.upBound = Globals.blackNestY
        Globals.downBound *= 2
        Globals.leftBound = Globals.blackNestX
        Globals.rightBound = Globals.redNestX

        self.underground = True
        
        self.direction = self.S
        self.sprite.setTextureRect(self.direction) # Update sprite direction.
        self.pos = list(self.pos)
        self.pos[0] = abs(Globals.blackNestX)
        self.pos[1] = abs(Globals.blackNestY)
        self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])
        
        self.queue.popleft()
        
    def posToTileCoords(self):
        return (self.pos[0]/32, self.pos[1]/32)

    def pickFoodUp(self, antLocationTile):
        self.parent.removeOneFood(antLocationTile)
        self.switchSprite(Globals.datadir + 'images/ants/yellowant_food.png')
        self.hasFood = True
        self.queue.popleft() #I hope this is right...

    def setFoodDown(self, antLocationTile):
        self.parent.spawnOneFood(antLocationTile)
        self.switchSprite(Globals.datadir + 'images/ants/yellowant.png')
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
        start = [int(self.pos[0] / 32), int(self.pos[1] / 32)]
        end = [int(self.newPos[0] / 32), int(self.newPos[1] / 32)]
        print start, end, self.pos, self.newPos
        # Start and end are the same tile, dont need to move.
        if start == end:
            self.queue.popleft()
            return
        
        map = self.getMap(start, end)
        
        a = AStar(map, MANHATTAN)
        q = collections.deque()
        
        a.step(q)

        #Oipo: surely the entire remove 32, add 32 deal that is done here can be optimised...I just am too lazy right now
        if self.underground:
            for i in range(len(a.path)):
                a.path[i] = list(a.path[i])
                a.path[i][1] += 32

        self.path.clear()
        self.path.extend(a.path)
        
        if not self.path:
            self.queue.popleft()
            return
        
        #Not sure what this does?
        #Oipo: I think it removes the starting location, namely the location of the ant?
        self.path.popleft()
        

        self.queue.popleft()
        self.queue.append(self.moveAlongPath)
    
    def findAltPath(self, avoid):
        start = [self.pos[0] / 32, self.pos[1] / 32]
        end = [self.newPos[0] / 32, self.newPos[1] / 32]
        # Start and end are the same tile, dont need to move.
        if start == end:
            self.queue.popleft()
            return

        if self.underground:
            start[1] -= Globals.mapheight
            end[1] -= Globals.mapheight
        
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

        add = 0
        if self.underground:
            add = Globals.mapheight

        for i in range(add, Globals.mapheight+add):
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
