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
# This is where all the globals of Open Ant are stored
#
# By Oipo (kingoipo@gmail.com)

#general
vbos = False
glwidget = None
player = None
overMap= None
datadir = "../data/"
pixelsize = 32
mapheight = 64 + 64 #ground + underground
mapwidth = 128

#nest coordinates
blackNestX = 0
blackNestY = -1 * pixelsize * (mapheight/2 + 1)
redNestX = -1 * pixelsize * (mapwidth/2 + 1)
redNestY = -1 * pixelsize * (mapheight/2 + 1)

#camera bounds
leftBound = 0
rightBound = -1 * mapwidth * pixelsize
upBound = 0
downBound = -1 * (mapheight/2) * pixelsize

#gui
#nothing here yet

#music
mediaobject = None

try:
    import PyQt4.phonon
    musicOn = True
except ImportError as e:
    musicOn = False
    
