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
# contains the panel to control the selection and playing of music.
#
# By Oipo (kingoipo@gmail.com)

import os
import random

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.phonon import *

import Globals

class fileItem(QListWidgetItem):

    def __init__(self, file, dir, panel):
        QListWidgetItem.__init__(self)
        self.file = file
        self.dir = dir

        self.setText(file)
        
class musicListWidget(QListWidget):

    def __init__(self, panel):
        QListWidget.__init__(self)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.panel = panel

class MusPanel(QDockWidget):
    '''Music Panel, shows the available music and allows the player to control it'''

    def __init__(self, mainWindow):
        super(QDockWidget, self).__init__(mainWindow)

        self.next = None
        self.contents = QWidget(self)
        self.musicList = musicListWidget(self)
        self.play = QPushButton("Play")
        self.stop = QPushButton("Stop")
        self.pause = QPushButton("Pause")
        self.shuffle = QCheckBox("Shuffle")
        
        self.addFilesInDir(Globals.datadir + "music")
        
        x = 0
        grid = QGridLayout()

        grid.addWidget(self.musicList, x, 0, 1, 3)
        x += 1
        
        grid.addWidget(Phonon.SeekSlider(Globals.mediaobject), x, 0, 1, 3)
        x += 1
        
        grid.addWidget(self.play, x, 0)
        grid.addWidget(self.stop, x, 1)
        grid.addWidget(self.pause, x, 2)
        x += 1
        
        grid.addWidget(self.shuffle, x, 0)
        x += 1

        self.contents.setLayout(grid)
        
        self.play.clicked.connect(self.playClicked)
        self.stop.clicked.connect(self.stopClicked)
        self.pause.clicked.connect(self.pauseClicked)
        Globals.mediaobject.aboutToFinish.connect(self.enqueueNext)
        Globals.mediaobject.currentSourceChanged.connect(self.updateList)
        
        self.setWindowTitle("Music Panel")
        self.setWidget(self.contents)
        mainWindow.addDockWidget(Qt.RightDockWidgetArea, self)

    def addFilesInDir(self, dir):
        fdir = os.listdir(dir)

        for file in fdir:
            if os.path.isdir(dir + '/' + file):
                self.addFilesInDir(dir + '/' + file)

        for file in fdir:
            if file[-3:] == "ogg":
                self.musicList.addItem(fileItem(file, dir, self))

    def updateList(self):
        if self.next != None:
            self.musicList.setCurrentItem(self.next)
        
    def enqueueNext(self):
        if self.shuffle.isChecked():
            rand = self.musicList.currentRow()
            count = self.musicList.count()
            
            while rand == self.musicList.currentRow() and count > 1:
                rand = random.randint(0, count-1)

            item = self.musicList.item(rand)
            Globals.mediaobject.enqueue(Phonon.MediaSource(item.dir + '/' + item.file))
        else:
            count = self.musicList.count()
            currentrow = self.musicList.currentRow()
            next = 0
            
            if currentrow + 1 < count:
                next = currentrow + 1
            
            item = self.musicList.item(next)
            Globals.mediaobject.enqueue(Phonon.MediaSource(item.dir + '/' + item.file))
            
        self.next = item
            
    def playClicked(self, checked):
        item = self.musicList.item(self.musicList.currentRow())
        
        if Globals.mediaobject.state() == Phonon.PausedState:
            Globals.mediaobject.play()
            return
        
        Globals.mediaobject.setCurrentSource(Phonon.MediaSource(item.dir + '/' + item.file))
        
        if Globals.mediaobject.state() != Phonon.PlayingState:
            Globals.mediaobject.play()
            
    def stopClicked(self, checked):
        Globals.mediaobject.stop()
    
    def pauseClicked(self, checked):
        if Globals.mediaobject.state() == Phonon.PausedState:
            Globals.mediaobject.play()
        if Globals.mediaobject.state() == Phonon.PlayingState:
            Globals.mediaobject.pause()
