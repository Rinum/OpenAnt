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
# convenience class
#
# By Oipo (kingoipo@gmail.com)

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype as ADT

import Globals

import numpy

class Image(object):
    '''
    Class for storing image data, position and some opengl stuff
    '''

    def __init__(self, imagepath, qimg, textureRect, drawRect, layer, hidden, dynamicity, glwidget):
        self.imagepath = imagepath
        self.drawRect = drawRect
        self.textureRect = textureRect
        self._layer = layer
        self.dynamicity = dynamicity
        self.textureId = None
        self.offset = None
        self.VBO = None
        self._hidden = hidden
        self.qimg = qimg
        self.glwidget = glwidget
        self.createLayer = False
        self.destroyed = False
        self.VBOData = numpy.zeros((8, 2), 'f')
        self.origtextrect = textureRect

        if self.glwidget.texext == GL_TEXTURE_2D:
            x = float(textureRect[0])/float(qimg.width())
            y = float(textureRect[1])/float(qimg.height())
            w = float(textureRect[2])/float(qimg.width())
            h = float(textureRect[3])/float(qimg.height())
            self.textureRect = [x, y, w, h]
            
        self.setVBOData()
            
    def destroy(self):
        if not self.destroyed:
            self.glwidget.deleteImage(self)
            self.destroyed = True
        else:
            print "attempted to destroy an image twice"

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, hide):
        if self._hidden != hide:
            self._hidden = hide
            self.glwidget.hideImage(self, hide)
            
    @property
    def layer(self):
        return self._layer
        
    @layer.setter
    def layer(self, newlayer):
        if self._layer != newlayer:
            self.glwidget.setLayer(self, newlayer)
            self._layer = newlayer
            
    def setHidden(self, hide):
        if self._hidden != hide:
            self._hidden = hide
            self.glwidget.hideImage(self, hide)
            
    def setX(self, x):
        drawRect = list(self.drawRect)
        drawRect[0] = x
        self.setDrawRect(drawRect)
        
    def setY(self, y):
        drawRect = list(self.drawRect)
        drawRect[1] = y
        self.setDrawRect(drawRect)
        
    def setDrawW(self, w):
        drawRect = list(self.drawRect)
        drawRect[2] = w
        self.setDrawRect(drawRect)
        
    def setDrawH(self, h):
        drawRect = list(self.drawRect)
        drawRect[3] = h
        self.setDrawRect(drawRect)
        
    def getW(self):
        return self.drawRect[2]
        
    def getH(self):
        return self.drawRect[3]

    def width(self):
        return self.drawRect[2]

    def height(self):
        return self.drawRect[3]

    def setDrawRect(self, drawRect):
        self.drawRect = drawRect

        if self.glwidget.vbos:
            self.setVBOData()

            glBindBuffer(GL_ARRAY_BUFFER_ARB, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER_ARB, int(self.offset*self.glwidget.vertByteCount/4), self.glwidget.vertByteCount, self.VBOData)
            
    def displaceDrawRect(self, displacement):
        self.drawRect = list(self.drawRect)
        self.drawRect[0] = self.drawRect[0] + displacement[0]
        self.drawRect[1] = self.drawRect[1] + displacement[1]
        self.setDrawRect(self.drawRect)

    def setTextureRect(self, textureRect):
        self.textureRect = textureRect
        if self.glwidget.texext == GL_TEXTURE_2D:
            x = float(textureRect[0])/float(self.qimg.width())
            y = float(textureRect[1])/float(self.qimg.height())
            w = float(textureRect[2])/float(self.qimg.width())
            h = float(textureRect[3])/float(self.qimg.height())
            self.textureRect = [x, y, w, h]
            
        if self.glwidget.vbos:
            self.setVBOData()

            glBindBuffer(GL_ARRAY_BUFFER_ARB, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER_ARB, int(self.offset*self.glwidget.vertByteCount/4), self.glwidget.vertByteCount, self.VBOData)
            
    def displaceTextureRect(self, displacement):
        if self.glwidget.texext == GL_TEXTURE_2D:
            x = float(self.origtextrect[0] + displacement[0])/float(self.qimg.width())
            y = float(self.origtextrect[1] + displacement[1])/float(self.qimg.height())
            w = float(self.origtextrect[2])/float(self.qimg.width())
            h = float(self.origtextrect[3])/float(self.qimg.height())
            self.textureRect = [x, y, w, h]
        self.setVBOData()
        glBindBuffer(GL_ARRAY_BUFFER_ARB, self.VBO)
        glBufferSubData(GL_ARRAY_BUFFER_ARB, int(self.offset*self.glwidget.vertByteCount/4), self.glwidget.vertByteCount, self.VBOData)

    def getVBOData(self):
        return self.VBOData
        
    def setVBOData(self):
        x, y, w, h = self.textureRect
        dx, dy, dw, dh = self.drawRect

        self.VBOData[0, 0] = x #tex
        self.VBOData[0, 1] = y+h

        self.VBOData[1, 0] = dx #vert
        self.VBOData[1, 1] = dy

        self.VBOData[2, 0] = x+w #tex
        self.VBOData[2, 1] = y+h

        self.VBOData[3, 0] = dx+dw #vert
        self.VBOData[3, 1] = dy

        self.VBOData[4, 0] = x+w
        self.VBOData[4, 1] = y

        self.VBOData[5, 0] = dx+dw
        self.VBOData[5, 1] = dy+dh

        self.VBOData[6, 0] = x
        self.VBOData[6, 1] = y

        self.VBOData[7, 0] = dx
        self.VBOData[7, 1] = dy+dh

    def __str__(self):
        text = "Image(", self.imagepath, self.drawRect, self.textureRect, self.layer, self.offset, self.textureId, self._hidden, ")"
        return str(text)
