#!/usr/bin/python
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
# starting point of Open Ant
#
# By: Oipo (kingoipo@gmail.com), Cibrong

import sys

from PyQt4.QtCore import QTime
from PyQt4.QtGui import QMainWindow, QApplication, QPalette, QColor

import Globals
from GLWidget import GLWidget
if Globals.musicOn:
    from PyQt4.phonon import Phonon
    from MusPanel import MusPanel
from LeftPanel import LeftPanel
from Map import Map

class MainWindow(QMainWindow):
    '''The main game window, holds all the panels and widgets.'''

    def __init__(self):
        QMainWindow.__init__(self)

        Globals.glwidget = GLWidget(self)
        self.setCentralWidget(Globals.glwidget)
        Globals.glwidget.makeCurrent() 
        
        if Globals.musicOn:
            print "Using music"
            Globals.mediaobject = Phonon.MediaObject(self)
            self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
            Phonon.createPath(Globals.mediaobject, self.audioOutput)
        
    def start(self):
        if Globals.musicOn:
            Globals.muspanel = MusPanel(self)
        
        # Load the main game menu panel.
        LeftPanel(self)
        
    def closeEvent(self, event):
        Globals.game_is_running = False
        event.accept()


class OpenAnt(QApplication):
    
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        
        # Set the default background color to a darker grey.
        self.setPalette(QPalette(self.palette().button().color(), QColor(192, 192, 192)))
    
        self.window = MainWindow()
        self.window.show()
        self.window.start()
        self.window.setWindowTitle('OpenAnt')
        
        # Game timer, used in the gameloop FPS calculations.
        self.game_timer = QTime()
        self.game_timer.start()
        
        # Draw map, set view to ground.
        self.map = Map()
        Globals.view = self.map.generateMap()
        self.map.spawnAnts()
        
        # Start the main loop.
        self.gameLoop()
        
    def gameLoop(self):
        TICKS_PER_SECOND = 20
        SKIP_TICKS = 1000 / TICKS_PER_SECOND
        MAX_FRAMESKIP = 5
        
        next_game_tick = self.getTickCount()
        Globals.game_is_running = True
        while Globals.game_is_running:
            loops = 0
            while self.getTickCount() > next_game_tick and loops < MAX_FRAMESKIP:
                self.updateGame()
                next_game_tick += SKIP_TICKS
                loops += 1
            interpolation = float(self.getTickCount() + SKIP_TICKS - next_game_tick) / float(SKIP_TICKS)
            self.updateDisplay(interpolation)

    def updateDisplay(self, interpolation):
       
        #lerp away
        if not 'nolerp' in sys.argv:
            if self.map.yellowAnt.moving:
                self.map.yellowAnt.lerpMoveSimple(interpolation)

        Globals.glwidget.updateGL()
        self.processEvents() # Let Qt process its events.

    def getTickCount(self):
        return self.game_timer.elapsed()

    def updateGame(self):
        self.map.update()

if __name__ == '__main__':
    OpenAnt()
