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
# Map Class

import os

from GLWidget import *
import Globals
from PyQt4.QtCore import *

class Ants():
    '''
    Class for generating ants
    '''
    def __init__(self,xpos,ypos):
        #initialize ant position to (xpos,ypos)
        self.pos = [xpos*32, ypos*32]
        self.newPos = [xpos*32, ypos*32]
        self.moving = False
        self.N = [0, 32, 32, 32]
        self.S = [32, 32, 32, 32]
        self.E = [64, 32, 32, 32]
        self.W = [96, 32, 32, 32]
        self.NW = [0, 0, 32, 32]
        self.NE = [32, 0, 32, 32]
        self.SW = [64, 0, 32, 32]
        self.SE = [96, 0, 32, 32]
        self.sprite = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellowant.png', 2, [32, 32, 32, 32], [self.pos[0], self.pos[1], 32, 32])
        self.sprite.setTextureRect(self.S)
        self.direction = self.S
        self.queue = []

    def move(self):
        x = self.newPos[0]
        y = self.newPos[1]
        newDirection = ""
        if self.pos[0] < x:
            self.pos[0] += 4
            newDirection = "E"
        elif self.pos[0] > x:
            self.pos[0] -= 4
            newDirection = "W"
        if self.pos[1] < y:
            self.pos[1] += 4
            newDirection = "S" + newDirection
        elif self.pos[1] > y:
            self.pos[1] -= 4
            newDirection = "N" + newDirection
        if self.pos[0] == x and self.pos[1] == y:
            self.queue = self.queue[1:] #Ant has reached its destination
        if newDirection != "":
            newDirection = "self." + newDirection
            self.direction = eval(newDirection)
            self.sprite.setTextureRect(self.direction) # Update sprite location.
        self.sprite.setDrawRect([self.pos[0], self.pos[1], 32, 32])
        
    def dig(self):
        print "WE CAN DIG!"
        self.queue = self.queue[1:] #Ant has dug