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
        self.xpos = xpos
        self.ypos = ypos
        self.sprite = None
        self.clickTime = 0#waiting for double click
        Globals.glwidget.mousePress.connect(self.getCoords)

    def drawAnt(self):
        #create ant
        self.sprite = Globals.glwidget.createImage(Globals.datadir+'images/yellowAnt.png', 2, [1, 1, -1, -1], [self.xpos, self.ypos, -1, -1])

    def move(self, x, y):
    	try: # We try and cancel any previous movements.
	    self.t.cancel()
	except:
	    pass
	# TODO: Implement a path finding algrothem like A*
        if self.xpos < x:
            self.xpos += 1 
        elif self.xpos > x:
            self.xpos -= 1 
        if self.ypos < y:
            self.ypos += 1 
        elif self.ypos > y:
            self.ypos -= 1
	self.sprite.setDrawRect([self.xpos, self.ypos, 24, 24]) # Update sprite location.
	if (self.xpos != x) or (self.ypos != y): # If we havn't reached our destination, Schedule another call to move.
	    self.t = Timer(0.03, self.move, (x, y))
	    self.t.start()

    def getCoords(self, button, x, y):
        '''
        On double click, move ant
        '''
	timeDiff = time.time()-self.clickTime
	self.clickTime = time.time()
	if( button == 1 and timeDiff<=0.25 ):
	    self.move(x, y)
