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
from OpenGL.GLU import *
from OpenGL.extensions import hasGLExtension
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype as ADT

#Only set these when creating non-development code
OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

import Globals

mod = False
try:
    print "Loading GLMod"
    import glmod
    mod = True
except:
    print "Failed!"
    pass

from Image import *

def nextPowerOfTwo(val):
    val -= 1
    val = (val >> 1) | val
    val = (val >> 2) | val
    val = (val >> 4) | val
    val = (val >> 8) | val
    val = (val >> 16) | val
    val += 1
    return val

class GLWidget(QGLWidget):
    '''
    Widget for drawing everything, and for catching mouse presses and similar
    '''

    mousePress = pyqtSignal(int, int, int) #button, x, y
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(640, 480)
	self.w = 640
        self.h = 480
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
        self.texext = GL_TEXTURE_RECTANGLE_ARB

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
	self.w = w
        self.h = h

    def initializeGL(self):
        '''
        Initialize GL
        '''
        global mod

        if not hasGLExtension("GL_ARB_texture_rectangle"):
            print "GL_TEXTURE_RECTANGLE_ARB not supported, switching to GL_TEXTURE_2D"
            self.texext = GL_TEXTURE_2D

        glEnable(self.texext)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0, 0, self.width(), self.height())
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)

        initok = False
        if mod:
            ret = glmod.init(self.texext)
            if ret == -1:
                print "Something terrible went wrong in initializing glmod"
                mod = False
            elif ret == -2:
                print "using gl module without VBO support"
            else:
                initok = True
                print "using gl module with VBO support"

        if mod and initok:
            if glInitVertexBufferObjectARB() and bool(glBindBufferARB):
                Globals.vbos = True
                print "VBO support initialised succesfully"
                self.VBO = int(glGenBuffersARB(1))
            else:
                print "VBO support initialisation failed, continuing without"

    #util functions
    def createImage(self, qimagepath, layer, textureRect, drawRect, hidden = False, dynamicity = GL_STATIC_DRAW_ARB):
        '''
        FILL IN LATER PLOX
        '''

        qimg = None
        layer = int(layer)

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

        image = Image(qimagepath, qimg, textureRect, drawRect, layer, hidden, dynamicity)

        texture = None
        found = False

        for qimgpath in self.qimages:
            if qimgpath == qimagepath and self.qimages[qimgpath][1] > 0:
                texture = self.qimages[qimgpath][0]
                found = True

        if found == False:
            if qimg == None:
                qimg = QImage(qimagepath)
                
            if self.texext == GL_TEXTURE_2D:
                w = nextPowerOfTwo(qimg.width())
                h = nextPowerOfTwo(qimg.height())
                if w != qimg.width() or h != qimg.height():
                    qimg = qimg.scaled(w, h)
                
            img = self.convertToGLFormat(qimg)
            texture = glGenTextures(1)
            imgdata = img.bits().asstring(img.numBytes())

            glBindTexture(self.texext, texture)

            glTexParameteri(self.texext, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(self.texext, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

            glTexImage2D(self.texext, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, imgdata);

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
            image.VBO = self.VBO

            self.fillBuffers(image)
            if len(self.qimages[qimagepath]) == 2:
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

        glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.VBO)

        if self.VBOBuffer <= size or image == None:
            self.VBOBuffer = nextPowerOfTwo(size+1)

            glBufferDataARB(GL_ARRAY_BUFFER_ARB, self.VBOBuffer*vertByteCount, None, GL_STATIC_DRAW_ARB)

            self.offset = 0

            for layer in self.layers:
                for img in self.images[layer]:
                    img.offset = int(float(self.offset)/vertByteCount*4)
                    VBOData = img.getVBOData()

                    glBufferSubDataARB(GL_ARRAY_BUFFER_ARB, self.offset, vertByteCount, VBOData)
                    self.offset += vertByteCount

        else:
            image.offset = int(float(self.offset)/vertByteCount*4)
            VBOData = image.getVBOData()

            glBufferSubDataARB(GL_ARRAY_BUFFER_ARB, self.offset, vertByteCount, VBOData)
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
        global mod

        if image.hidden:
            return

        x, y, w, h = image.textureRect
        dx, dy, dw, dh = image.drawRect

        cx, cy = self.camera

        # Culling
        if (dx * self.zoom > self.w - cx) or (dy * self.zoom > self.h - cy) or ((dx + dw) * self.zoom < 0-cx) or ((dy + dh) * self.zoom < 0-cy):
            return

        if mod:
            glmod.drawTexture(image.textureId, dx, dy, dw, dh, x, y, w, h)
        else:
            self.drawTexture(image.textureId, dx, dy, dw, dh, x, y, w, h)

    def drawTexture(self, texture, dx, dy, dw, dh, x, y, w, h):
        '''
        texture is an int
        textureRect is a list of size 4, determines which square to take from the texture
        drawRect is a list of size 4, is used to determine the drawing size
        '''

        glBindTexture(self.texext, texture)

        glBegin(GL_QUADS)
        #Top-left vertex (corner)
        glTexCoord2f(x, y+h) #image/texture
        glVertex3f(dx, dy, 0) #screen coordinates

        #Bottom-left vertex (corner)
        glTexCoord2f(x+w, y+h)
        glVertex3f((dx+dw), dy, 0)

        #Bottom-right vertex (corner)
        glTexCoord2f(x+w, y)
        glVertex3f((dx+dw), (dy+dh), 0)

        #Top-right vertex (corner)
        glTexCoord2f(x, y)
        glVertex3f(dx, (dy+dh), 0)
        glEnd()
        
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
