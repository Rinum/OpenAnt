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

from random import *

class Map():
    '''
    Class for generating maps
    '''
    def __init__(self):
        #Ground tiles
        self.groundTilesPath = Globals.datadir+'images/ground/'
        self.groundTiles = []

        #Foliage tiles
        self.foliageTilesPath = Globals.datadir+'images/foliage/'
        self.foliageTiles = []

        #Populate list of ground tiles
        dirList=os.listdir(self.groundTilesPath)
        for fname in dirList:
            self.groundTiles.append(fname)

        #Populate list of foliage tiles
        dirList=os.listdir(self.foliageTilesPath)
        for fname in dirList:
            self.foliageTiles.append(fname)
    
    def generateMap(self):
        for x in range(64):
            for y in range(48):
                if(randint(0,10)>8):
                    Globals.glwidget.createImage(self.foliageTilesPath + self.foliageTiles[randint(0, len(self.foliageTiles)-1)], 1, [1, 1, -1, -1], [x*24, y*24, -1, -1])
                Globals.glwidget.createImage(self.groundTilesPath + self.groundTiles[randint(0, len(self.groundTiles)-1)], 0, [1, 1, -1, -1], [x*24, y*24, -1, -1])
