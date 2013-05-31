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
# The main panel of the game.
#
# By Cibrong

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from HealthWidget import *
import Globals

class PictureButton(QAbstractButton):
    def __init__(self, parent = None, clickedCall = "", pressedCall = "", icon = Globals.datadir + "images/button.png"):
        super(PictureButton, self).__init__()
        self.icon = QImage(icon)
        if not clickedCall == "":
            clickedCall = "parent." + clickedCall
            self.connect(self, SIGNAL("clicked()"), eval(clickedCall))
        if not pressedCall == "":
            pressedCall = "parent." + pressedCall
            self.connect(self, SIGNAL("pressed()"), eval(pressedCall))
        
    def sizeHint(self):
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return QSize(self.icon.width(), self.icon.height())
        
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawButton(qp)
        qp.end()
        
    def drawButton(self, qp):
        qp.setPen(Qt.black)
        qp.setBrush(Qt.SolidPattern)
        rectangle = QRect(1, 1, self.icon.width(), self.icon.height())
        qp.drawImage(rectangle, self.icon)

class LeftPanel(QDockWidget):
    def __init__(self, mainWindow):
        super(LeftPanel, self).__init__()
        
        # Gets rid of the title bar.
        self.setTitleBarWidget(QWidget())
        # Title still shows up in the right click menu.
        self.setWindowTitle("Main Panel")
        
        # Create the layout.
        self.contents = QWidget(self)
        # Don't allow resizing closing or undocking.
        self.setFeatures(QDockWidget.DockWidgetFeatures(QDockWidget.NoDockWidgetFeatures))
        # Add the health view.
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()
        
        hbox1.addWidget(PictureButton(self, "help","",Globals.datadir + "images/UI/help.png"))
        hbox1.addWidget(PictureButton(self, "experiment","",Globals.datadir + "images/UI/experiment.png"))
        vbox.addLayout(hbox1)
        
        hbox2.addWidget(PictureButton(self, "map","",Globals.datadir + "images/UI/map.png"))
        vbox.addLayout(hbox2)
        
        hbox3.addWidget(PictureButton(self, "blackNest","",Globals.datadir + "images/UI/blackNest.png"))
        hbox3.addWidget(PictureButton(self, "redNest","",Globals.datadir + "images/UI/redNest.png"))
        vbox.addLayout(hbox3)
        
        hbox4.addWidget(PictureButton(self, "yellowAnt","",Globals.datadir + "images/UI/yellowAnt.png"))
        hbox4.addWidget(PictureButton(self, "spider","",Globals.datadir + "images/UI/spider.png"))
        vbox.addLayout(hbox4)
        
        hbox5.addWidget(PictureButton(self, "blackQueen","",Globals.datadir + "images/UI/blackQueen.png"))
        hbox5.addWidget(PictureButton(self, "redQueen","",Globals.datadir + "images/UI/redQueen.png"))
        vbox.addLayout(hbox5)
        
        vbox.addWidget(HealthWidget())
        
        self.contents.setLayout(vbox)
        self.setWidget(self.contents)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)
        
    def help(self):
        print "Help!"
        
    def experiment(self):
        print "Experiment!"

    def map(self):
        print "Map!"
        
    def blackNest(self):
        print "Black Ant Nest!"
    
    def redNest(self):
        print "Red Ant Nest!"
        
    def yellowAnt(self):
        print "Yellow Ant!"
        
    def spider(self):
        print "Spider! Kill it with fire!"
        
    def blackQueen(self):
        print "Black Ant's Queen!"
        
    def redQueen(self):
        print "Red Ant's Queen!"
        
        
