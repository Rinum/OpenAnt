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
        self.setFeatures(QDockWidget.DockWidgetFeatures(QDockWidget.NoDockWidgetFeatures));
        # Add the health view.
        self.wid = HealthWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.wid)
        self.contents.setLayout(vbox)
        self.setWidget(self.contents)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)
