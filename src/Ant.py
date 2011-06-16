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

class Ant():
    '''
    Class for generating ants
    '''
    def __init__(self, xpos, ypos, tiles, sprite):
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
        self.queue = []
        
        self.tiles = tiles
        self.speed = 4
        
    def setSprite(self, sprite):
        self.sprite = sprite
        
    def move(self):
        if len(self.path) or self.nextPos[0] != -1:
            if (self.nextPos[0] == -1 or (self.pos[0] == self.nextPos[0] and self.pos[1] == self.nextPos[1])) and len(self.path):
                _pos = self.path.pop()
                self.nextPos[0] = _pos[0] * 32
                self.nextPos[1] = _pos[1] * 32
            newDirection = ""
            if self.pos[0] < self.nextPos[0]:
                # This makes it so that your speed does not need to be a factor of 32 (or whatever the tile size is)
                if self.nextPos[0] - self.pos[0] < self.speed:
                    self.pos[0] += self.nextPos[0] - self.pos[0]
                else:
                    self.pos[0] += self.speed
                newDirection = "E"
            if self.pos[0] > self.nextPos[0]:
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
            if self.pos[1] > self.nextPos[1]:
                if self.pos[1] - self.nextPos[1] < self.speed:
                    self.pos[1] -= self.pos[1] - self.nextPos[1]
                else:
                    self.pos[1] -= self.speed
                newDirection = "N" + newDirection

            if newDirection != "":
                newDirection = "self." + newDirection
                self.direction = eval(newDirection)
                self.sprite.setTextureRect(self.direction) # Update sprite location.
            self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])
        if self.pos[0] == self.nextPos[0] and self.pos[1] == self.nextPos[1] and len(self.path) == 0:
            self.queue = self.queue[1:] #Ant has reached its destination

    def dig(self):
        print "WE CAN DIG!"
        self.queue = self.queue[1:] #Ant has dug
        
    # Find a path using A* Manhattan
    def findPath(self):
        start = [self.pos[0] / 32, self.pos[1] / 32]
        end = [self.newPos[0] / 32, self.newPos[1] / 32]
        
        # Start and end are the same tile, dont need to move.
        if start == end:
            self.queue = self.queue[1:]
            return
        
        map = self.getMap(start, end)
        
        a = AStar(map, MANHATTAN)
        q = collections.deque()
        
        a.step(q)

        self.path = a.path
        
        if not len(self.path):
            self.queue = self.queue[1:]
            return
        
        del self.path[0]
        self.path.reverse()
        
        self.queue = self.queue[1:]
        self.queue.append(self.move)
        
    def getMap(self, start, end):
        """Generate a string representation of the map."""
        output = ""

        for i in range(Globals.mapheight):
            for j in range(Globals.mapwidth):
                if start[0] == j and start[1] == i:
                    output += SOURCE
                elif end[0] == j and end[1] == i:
                    output += TARGET
                elif self.tiles[j][i].isPassable():
                    output += NORMAL
                else:
                    output += BLOCKED
            output += "\n"

        return output