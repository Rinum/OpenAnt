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


class Food():
    '''
    Class for food sprites
    '''
    def __init__(self, xpos, ypos, sprite):
        # Current position.
        self.pos = [xpos * 32, ypos * 32]

        self.sprite = sprite
        self.sprite.setTextureRect([32, 32, 32, 32])

