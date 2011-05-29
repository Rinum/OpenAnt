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
# WorkerAnt class
#
# Abstraction test

from GLWidget import *
from PyQt4.QtCore import *
from Ant import *

class WorkerAnt(Ant):
    def __init__(self, xpos, ypos, tiles, sprite):
        #initialize ant position to (xpos,ypos)
        self.pos = [xpos * 32, ypos * 32]
        self.newPos = [xpos * 32, ypos * 32]
        self.moving = False
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
        self.speed = 8