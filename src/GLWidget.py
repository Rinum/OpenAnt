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
# Takes care of drawing images, with optionally glmod to speed things up
#
# By Oipo (kingoipo@gmail.com)

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype as ADT

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import Globals

mod = False
try:
    import glmod
    mod = True
except:
    pass

from Image import *

class GLWidget(QGLWidget):
    '''
    Widget for drawing everything, and for catching mouse presses and similar
    '''

    mousePress = pyqtSignal(int, int, int) #button, x, y
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(640, 480)
        self.x = 0
        self.images = dict()
        self.lastMousePos = [0, 0]
        self.camera = [0, 0]
        self.layers = []
        self.zoom = 1
        self.VBO = None
        self.VBOBuffer = 0
        self.offset = 0
        self.vbolist = []
        self.qimages = {}

    #GL functions
    def paintGL(self):
        '''
        Drawing routine
        '''
        
        glClear(GL_COLOR_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(self.camera[0], self.camera[1], 0)
        glScaled(self.zoom, self.zoom, 1)

        if Globals.vbos:
            glmod.drawVBO()
        else:
            for layer in self.layers:
                for img in self.images[layer]:
                    self.drawImage(img)

        glScaled(1/self.zoom, 1/self.zoom, 1)
        glTranslatef(-self.camera[0], -self.camera[1], 0)
        glPopMatrix()

    def resizeGL(self, w, h):
        '''
        Resize the GL window 
        '''
        
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)

    def initializeGL(self):
        '''
        Initialize GL
        '''

        glEnable(GL_TEXTURE_RECTANGLE_ARB)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0, 0, self.width(), self.height())
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)

        if mod and glInitVertexBufferObjectARB():
            glmod.init()
            Globals.vbos = True
            print "using VBOs"
            self.VBO = int(glGenBuffersARB(1))

        for x in range(2):
            for y in range(2):
                self.createImage(Globals.datadir + "images/test.png", 3, [0, 0, -1, -1], [x*16, y*16, -1, -1])

    #util functions
    def createImage(self, qimagepath, layer, textureRect, drawRect, hidden = False, dynamicity = GL_STATIC_DRAW_ARB):
        '''
        FILL IN LATER PLOX
        '''

        qimg = None

        if textureRect[2] == -1:
            if qimg == None:
                qimg = QImage(qimagepath)
            textureRect[2] = qimg.width()

        if textureRect[3] == -1:
            if qimg == None:
                qimg = QImage(qimagepath)
            textureRect[3] = qimg.height()

        if drawRect[2] == -1:
            if qimg == None:
                qimg = QImage(qimagepath)
            drawRect[2] = qimg.width()

        if drawRect[3] == -1:
            if qimg == None:
                qimg = QImage(qimagepath)
            drawRect[3] = qimg.height()

        image = Image(qimagepath, textureRect, drawRect, layer, hidden, dynamicity)

        texture = None
        found = False

        for qimgpath in self.qimages:
            if qimgpath == qimagepath and self.qimages[qimgpath][1] > 0:
                texture = self.qimages[qimgpath][0]
                found = True

        if found == False:
            if qimg == None:
                qimg = QImage(qimagepath)
            img = self.convertToGLFormat(qimg)
            texture = glGenTextures(1)
            imgdata = img.bits().asstring(img.numBytes())

            glBindTexture(GL_TEXTURE_RECTANGLE_ARB, texture)

            glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_RECTANGLE_ARB, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

            glTexImage2D(GL_TEXTURE_RECTANGLE_ARB, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, imgdata);

            self.qimages[qimagepath] = [texture, 1] #texture, reference count
        else:
            self.qimages[qimagepath][1] += 1

        image.textureId = texture

        if layer not in self.images:
            self.images[layer] = []
            self.layers = self.images.keys()
            self.layers.sort()

        self.images[layer].append(image)

        if Globals.vbos:
            print self.VBO, self.qimages[qimagepath], image
            image.VBO = self.VBO

            self.fillBuffers(image)
            self.qimages[qimagepath].append(image.offset)

            self.calculateVBOList(image)

        return image

    def fillBuffers(self, image = None):
        '''
        ALSO FILL IN LATER...PLOX
        '''
        size = 0
        vertByteCount = ADT.arrayByteCount(numpy.zeros((8, 2), 'f'))

        for layer in self.layers:
            size += len(self.images[layer])

        print vertByteCount, size, self.VBOBuffer

        glBindBuffer(GL_ARRAY_BUFFER_ARB, self.VBO)

        if self.VBOBuffer <= size or image == None:
            self.VBOBuffer = glmod.nextPowerOfTwo(size)

            glBufferData(GL_ARRAY_BUFFER_ARB, self.VBOBuffer*vertByteCount, None, GL_STATIC_DRAW_ARB)

            self.offset = 0

            for layer in self.layers:
                for img in self.images[layer]:
                    img.offset = int(float(self.offset)/vertByteCount*4)
                    VBOData = img.getVBOData()

                    print img.offset

                    glBufferSubData(GL_ARRAY_BUFFER_ARB, self.offset, vertByteCount, VBOData)
                    self.offset += vertByteCount

        else:
            image.offset = int(float(self.offset)/vertByteCount*4)
            VBOData = image.getVBOData()

            print image.offset

            glBufferSubData(GL_ARRAY_BUFFER_ARB, self.offset, vertByteCount, VBOData)
            self.offset += vertByteCount

    def deleteImage(self, image):
        '''
        INACCURATE. IGNORE THIS COMMENT.
        '''

        self.qimages[image.imagepath][1] -= 1

        if self.qimages[image.imagepath][1] <= 0:
            glDeleteTextures(image.textureId)

        self.images[image.layer].remove(image)

        if Globals.vbos:
            self.calculateVBOList()

    def drawImage(self, image):
        if image.hidden:
            return

        if mod:
            x, y, w, h = image.textureRect
            dx, dy, dw, dh = image.drawRect

            glmod.drawTexture(image.textureId, dx, dy, dw, dh, x, y, w, h)
        else:
            self.drawTexture(image.textureId, image.textureRect, image.drawRect)

    def drawTexture(self, texture, textureRect, drawRect):
        '''
        texture is an int
        textureRect is a list of size 4, determines which square to take from the texture
        drawRect is a list of size 4, is used to determine the drawing size
        '''

        glBindTexture(GL_TEXTURE_RECTANGLE_ARB, texture)

        x, y, w, h = textureRect
        dx, dy, dw, dh = drawRect

        glBegin(GL_QUADS);
        #Top-left vertex (corner)
        glTexCoord2i(x, y+h); #image/texture
        glVertex3f(dx, dy, 0); #screen coordinates

        #Bottom-left vertex (corner)
        glTexCoord2i(x+w, y+h);
        glVertex3f((dx+dw), dy, 0);

        #Bottom-right vertex (corner)
        glTexCoord2i(x+w, y);
        glVertex3f((dx+dw), (dy+dh), 0);

        #Top-right vertex (corner)
        glTexCoord2i(x, y);
        glVertex3f(dx, (dy+dh), 0);
        glEnd();
        
    def calculateVBOList(self, image = None):
        '''
        Create the VBO list to be passed on to the module for drawing
        vbolist could possibly be a multi-layered tuple, one tuple per layer.
        So that it doesn't have to be recalculated every time one single image is changed.
        '''
        self.vbolist = [self.VBO, ADT.arrayByteCount(numpy.zeros((2, 2), 'f'))]
        for layer in self.layers:
            for img in self.images[layer]:
                if img.hidden:
                    continue
                self.vbolist.append(img.textureId)
                self.vbolist.append(img.offset)
        glmod.setVBO(tuple(self.vbolist))

    def hideImage(self, image, hide):
        '''
        This function should only be called from image.py
        Use Image.hide() instead.
        '''
        if Globals.vbos:
            self.calculateVBOList()

    def mouseMoveEvent(self, mouse):
        self.camera[0] += mouse.pos().x() - self.lastMousePos[0]
        self.camera[1] += mouse.pos().y() - self.lastMousePos[1]
        self.lastMousePos = [mouse.pos().x(), mouse.pos().y()]

        mouse.accept()

    def mousePressEvent(self, mouse):
        self.lastMousePos = (mouse.pos().x(), mouse.pos().y())

        button = -1

        if mouse.button() == Qt.LeftButton:
            button = 1
        elif mouse.button == Qt.RightButton:
            button = 2
        elif mouse.button == Qt.MidButton:
            button = 3

        self.mousePress.emit(button, (mouse.pos().x()-self.camera[0])/self.zoom, (mouse.pos().y()-self.camera[1])/self.zoom)

        mouse.accept()

    def wheelEvent(self, mouse):
        oldCoord = [mouse.pos().x(), mouse.pos().y()]
        oldCoord[0] *= float(1)/self.zoom
        oldCoord[1] *= float(1)/self.zoom

        oldCoord2 = self.camera
        oldCoord2[0] *= float(1)/self.zoom
        oldCoord2[1] *= float(1)/self.zoom

        if mouse.delta() < 0:
            self.zoom -= 0.15
        elif mouse.delta() > 0:
            self.zoom += 0.15

        if self.zoom < 0.30:
            self.zoom = 0.30
        elif self.zoom > 4:
            self.zoom = 4

        self.camera[0] = oldCoord2[0] * self.zoom - ((oldCoord[0]*self.zoom)-mouse.pos().x())
        self.camera[1] = oldCoord2[1] * self.zoom - ((oldCoord[1]*self.zoom)-mouse.pos().y())

        mouse.accept()
