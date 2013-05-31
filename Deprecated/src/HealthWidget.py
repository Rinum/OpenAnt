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
# Qt widget that displays the current health of the red and black hive and the yellow ant.
#
# By Cibrong

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HealthWidget(QWidget):
    def __init__(self):      
        super(HealthWidget, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.setMinimumWidth(100)
        self.redHealth = 43.34;
        self.blackHealth = 10;
        self.yellowHealth = 55;
        #TODO Signals to update the health bars.
        self.connect(self, SIGNAL("updateRedHealth(int)"), self.setRedHealth)
        self.connect(self, SIGNAL("updateBlackHealth(int)"), self.setBlackHealth)
        self.connect(self, SIGNAL("updateYellowHealth(int)"), self.setYellowHealth)
        
    def setRedHealth(self, val):
        self.redHealth = val;
        
    def setBlackHealth(self, val):
        self.BlackHealth = val;
        
    def setYellowHealth(self, val):
        self.YellowHealth = val;
        
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
        
    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()
        
        font = QFont('Serif', 10, QFont.Bold)
        font.setStyleStrategy(QFont.StyleStrategy(QFont.ForceOutline|QFont.OpenGLCompatible))
        qp.setFont(font)
        
        metrics = qp.fontMetrics()
        fw = metrics.width("Health")
        qp.setPen(Qt.black)
        qp.drawText((w/2)-(fw/2), 10, "Health")
        
        qDrawWinPanel(qp, w/8, 20, 75, 150, QApplication.palette(), True, QBrush(Qt.white))

        fw = metrics.width("Y")
        fh = metrics.height()
        qp.setPen(Qt.yellow)
        qp.drawText((w/4)-(fw/2), 171 + fh, "Y")
        qp.setPen(Qt.black)
        qp.drawText(((w/4)-(fw/2)) + 25, 171 + fh, "B")
        qp.setPen(Qt.red)
        qp.drawText(((w/4)-(fw/2)) + 50, 171 + fh, "R")
        
        # Yellow health bar.
        qp.setPen(Qt.black)
        qp.setBrush(Qt.NoBrush)
        rectangle = QRectF((w/4)-(fw/2), 25.0, 10.0, 140.0)
        qp.drawRect(rectangle)
        if self.yellowHealth:
            qp.setPen(Qt.yellow)
            qp.setBrush(Qt.yellow)
            rectangle = QRectF(((w/4)-(fw/2) + 1), 24 + (140 - ((self.yellowHealth/100.0)*140.0)), 8.0, (self.yellowHealth/100.0)*140.0)
            qp.drawRect(rectangle)
            
        # Black health bar.
        qp.setPen(Qt.black)
        qp.setBrush(Qt.NoBrush)
        rectangle = QRectF(((w/4)-(fw/2)) + 25, 25.0, 10.0, 140.0)
        qp.drawRect(rectangle)
        if self.blackHealth:
            qp.setPen(Qt.black)
            qp.setBrush(Qt.black)
            rectangle = QRectF((((w/4)-(fw/2)) + 26), 24 + (140 - ((self.blackHealth/100.0)*140.0)), 8.0, (self.blackHealth/100.0)*140.0)
            qp.drawRect(rectangle)
            
        # Red health bar.
        qp.setPen(Qt.black)
        qp.setBrush(Qt.NoBrush)
        rectangle = QRectF((w/4)-(fw/2)+50, 25.0, 10.0, 140.0)
        qp.drawRect(rectangle)
        if self.redHealth:
            qp.setPen(Qt.red)
            qp.setBrush(Qt.red)
            rectangle = QRectF(((w/4)-(fw/2) + 51), 24 + (140 - ((self.redHealth/100.0)*140.0)), 8.0, (self.redHealth/100.0)*140.0)
            qp.drawRect(rectangle)
