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
#
# Transforms a slice of the map (along any axis) and generates a
# viewable repersentation
#
# By phire (phire@gmail.com)

import Globals
import numpy

class View():
    def __init__(self, mapSlice, hidden = False):
        self.tiles = numpy.empty_like(mapSlice)
        self.width = len(mapSlice)
        self.height= len(mapSlice[0])

        Globals.glwidget.reserveVBOSize(self.width*self.height)

        for x in range(self.width):
            for y in range(self.height):
                self.tiles[x][y] = Globals.glwidget.createImage(mapSlice[x,y].image, 0, [1, 1, -1, -1], [x*Globals.pixelsize, y*Globals.pixelsize, -1, -1], hidden)
    
    def delete(self):
	# Delete all images
        pass # not implemented yet.

    def ground(self, x=0, y=0):
        Globals.leftBound = 0
        Globals.rightBound = -1 * Globals.mapwidth * Globals.pixelsize
        Globals.upBound = 0
        Globals.downBound = -1 * (Globals.mapheight/2) * Globals.pixelsize
        Globals.glwidget.camera[0] = x
        Globals.glwidget.camera[1] = y       

    def blackNest(self, x=Globals.blackNestX, y=Globals.blackNestY):
        Globals.leftBound = 0
        Globals.rightBound = Globals.redNestX
        Globals.upBound = Globals.blackNestY
        Globals.downBound = -1 * Globals.mapheight * Globals.pixelsize
        Globals.glwidget.camera[0] = x
        Globals.glwidget.camera[1] = y
        
    def redNest(self, x=Globals.redNestX,y=Globals.redNestY):
        Globals.leftBound = Globals.redNestY
        Globals.rightBound = -1 * Globals.mapwidth * Globals.pixelsize
        Globals.upBound = Globals.redNestY
        Globals.downBound = -1 * Globals.mapheight * Globals.pixelsize
        Globals.glwidget.camera[0] = x
        Globals.glwidget.camera[1] = y
