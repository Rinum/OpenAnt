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
    def __init__(self, mapSlice):
        self.tiles = numpy.empty_like(mapSlice)

        for x in range(len(mapSlice)):
            for y in range(len(mapSlice[0])):
                Globals.glwidget.createImage(mapSlice[x,y].image, 0, [1, 1, -1, -1], [x*24, y*24, -1, -1])

    def delete(self):
	# Delete all images
        pass # not implemented yet.
