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
# By Oipo (kingoipo@gmail.com)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from GLWidget import *
from Map import *
import Globals

if Globals.musicOn:
    from PyQt4.phonon import *
    from MusPanel import *
from LeftPanel import *

from Map import *
from Ant import *

class MainWindow(QMainWindow):
    '''Wrapper class for...well, the game? Maybe this needs to be called the game engine then'''

    def __init__(self):
        '''
        Only initialize critical components(like opengl) here, use start() for anything else
        '''
        QMainWindow.__init__(self)

        Globals.glwidget = GLWidget(self)
        self.setCentralWidget(Globals.glwidget)
        Globals.glwidget.makeCurrent() 
        
        if Globals.musicOn:
            print "Using music"
            Globals.mediaobject = Phonon.MediaObject(self)
            self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
            Phonon.createPath(Globals.mediaobject, self.audioOutput)

        self.map = Map() #map class

        self.drawTimer = QTimer()
        self.drawTimer.timeout.connect(self.drawTimerTimeout)
        self.drawTimer.start(15)
        
    def start(self):
        if Globals.musicOn:
            Globals.muspanel = MusPanel(self)
            
        LeftPanel(self)
        
        #draw map... set view to ground
        Globals.view = self.map.generateMap()
        self.map.spawnAnts()

    def drawTimerTimeout(self):
        self.map.update()
        Globals.glwidget.updateGL()
 

if __name__ == '__main__':
    app = QApplication(['OpenAnt'])
    # Set the default background color to a darker grey.
    app.setPalette(QPalette(app.palette().button().color(), QColor(192, 192, 192)))
    
    QPalette.Window
    window = MainWindow()
    window.show()
    window.start()
    app.exec_()
