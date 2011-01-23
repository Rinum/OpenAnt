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

import time
from threading import Timer

class Ants():
    '''
    Class for generating ants
    '''
    def __init__(self,xpos,ypos):
        #initialize ant position to (xpos,ypos)
        self.xpos = xpos*24
        self.ypos = ypos*24
        self.N = [0, 24, 24, 24]
        self.S = [24, 24, 24, 24]
        self.E = [48, 24, 24, 24]
        self.W = [72, 24, 24, 24]
        self.NW = [0, 0, 24, 24]
        self.NE = [24, 0, 24, 24]
        self.SW = [48, 0, 24, 24]
        self.SE = [72, 0, 24, 24]
        self.sprite = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellowant.png', 2, [24, 24, 24, 24], [self.xpos, self.ypos, 24, 24])
        self.sprite.setTextureRect(self.S)
        self.direction = self.S
        Globals.glwidget.mousePress.connect(self.getCoords)

    def move(self, x, y):
        try: # We try and cancel any previous movements.
	    self.t.cancel()
	except:
	    pass
	# TODO: Implement a path finding algrothem like A*
	newDirection = ""
        if self.xpos/24 < x:
            self.xpos += 1
            newDirection = "E"
        elif self.xpos/24 > x:
            self.xpos -= 1
            newDirection = "W"
        if self.ypos/24 < y:
            self.ypos += 1
            newDirection = "S" + newDirection
        elif self.ypos/24 > y:
            self.ypos -= 1
            newDirection = "N" + newDirection
        if(newDirection != ""):
	    newDirection = "self." + newDirection
            self.direction = eval(newDirection)
	self.sprite.setTextureRect(self.direction) # Update sprite location.
        self.sprite.setDrawRect([self.xpos, self.ypos, 24, 24]) # Update sprite location.
        if (self.xpos != x) or (self.ypos != y): # If we havn't reached our destination, Schedule another call to move.
            self.t = Timer(0.03, self.move, (x, y))
            self.t.start()

    def getCoords(self, button, x, y):
        '''
        On click, move ant
        '''
	if button == 1:
            self.move(x/24, y/24)
