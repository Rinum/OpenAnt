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
        self.sprite = None
        self.clickTime = 0 #waiting for double click
        self.direction = "self.S"
        Globals.glwidget.mousePress.connect(self.getCoords)

    def drawAnt(self):
        #create ant
        self.N = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/N.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.S = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/S.png', 2, [1, 1, -1, -1], [self.xpos, self.ypos, -1, -1])
        self.E = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/E.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.W = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/W.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.NE = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/NE.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.NW = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/NW.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.SE = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/SE.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.SW = Globals.glwidget.createImage(Globals.datadir + 'images/ants/yellow/SW.png', 2, [1, 1, -1, -1], [-100, -100, -1, -1])
        self.sprite = self.S

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
        if newDirection != "":
            newDirection = "self." + newDirection
            if self.direction != newDirection:
                self.sprite.setDrawRect([-100, -100, 24, 24]) # Update sprite location.
                self.sprite = eval(newDirection)
                self.direction = newDirection
                self.sprite.setDrawRect([self.xpos, self.ypos, 24, 24]) # Update sprite location.
            if self.xpos != x or self.ypos != y: # If we havn't reached our destination, Schedule another call to move.
                self.t = Timer(0.03, self.move, (x, y))
                self.t.start()

    def getCoords(self, button, x, y):
        '''
        On double click, move ant
        '''
        timeDiff = time.time() - self.clickTime
        self.clickTime = time.time()
        if button == 1 and timeDiff <= 0.25:
            self.move(x/24, y/24)
