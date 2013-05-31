# -*- coding: utf-8 -*-
#
#glWidget - Takes care of drawing images, with optionally glmod to speed things up
#
#By Oipo (kingoipo@gmail.com)

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.extensions import hasGLExtension
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.ARB.texture_compression_rgtc import *
from OpenGL.arrays import ArrayDatatype as ADT

#Only set these when creating non-development code
OpenGL.ERROR_CHECKING = False
OpenGL.ERROR_LOGGING = False

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *

mod = False
try:
    print "Loading GLMod"
    import glmod
    mod = True
except Exception as e:
    print "Failed!", e
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

    mousePress = pyqtSignal(int, int, int) #x, y, button
    mouseRelease = pyqtSignal(int, int, int) #x, y, button
    mouseMove = pyqtSignal(int, int) #x, y
    
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)

        self.setMinimumSize(640, 480)
        self.w = 640
        self.h = 480
        self.images = dict()
        self.lastMousePos = [0, 0]
        self.camera = [0, 0]
        self.layers = []
        self.zoom = 1
        self.VBO = None
        self.vbos = False
        self.VBOBuffer = 0
        self.offset = 0
        self.ctrl = False
        self.shift = False
        self.qimages = {}
        self.texext = GL_TEXTURE_2D
        self.error = False
        self.texts = []
        self.textid = 0
        self.vertByteCount = ADT.arrayByteCount(numpy.zeros((8, 2), 'f'))
        self.movecam = False

        #default settings, though overriden in initializeGL by fieldtemp
        self.npot = 3
        self.anifilt = 0
        self.compress = False
        self.magfilter = GL_NEAREST
        self.mipminfilter = GL_NEAREST_MIPMAP_NEAREST
        self.minfilter = GL_NEAREST

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True) #this may be the fix for a weird problem with leaveevents

    #GL functions
    def paintGL(self):
        '''
        Drawing routine
        '''

        glClear(GL_COLOR_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(self.camera[0], self.camera[1], 0)
        glScaled(self.zoom, self.zoom, 1)

        if self.vbos:
            glmod.drawVBO()
        else:
            for layer in self.layers:
                for img in self.images[layer]:
                    self.drawImage(img)

        for text in self.texts:
            _split = text[1].split("\n")
            brk = lambda x, n, acc=[]: brk(x[n:], n, acc+[(x[:n])]) if x else acc
            split = []
            for item in _split:
                split.extend(brk(item, 35))
            if len(split[0]) == 0:
                split.pop(0)
            pos = -16 * (len(split) - 1)
            for t in split:
                if len(t) == 0:
                    continue
                
                self.renderText(float(text[2][0]), float(text[2][1])+pos, 0, t)
                pos += 16

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
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        self.w = w
        self.h = h

    #ugly conversion function :(
    def interpretString(self, string):
        if string == "GL_COMPRESSED_RG_RGTC2":
            return GL_COMPRESSED_RG_RGTC2
        if string == "GL_NEAREST":
            return GL_NEAREST
        if string == "GL_LINEAR":
            return GL_LINEAR
        if string == "GL_NEAREST_MIPMAP_NEAREST":
            return GL_NEAREST_MIPMAP_NEAREST
        if string == "GL_NEAREST_MIPMAP_LINEAR":
            return GL_NEAREST_MIPMAP_LINEAR
        if string == "GL_LINEAR_MIPMAP_NEAREST":
            return GL_LINEAR_MIPMAP_NEAREST
        if string == "GL_LINEAR_MIPMAP_LINEAR":
            return GL_LINEAR_MIPMAP_LINEAR
        return string

    def initializeGL(self):
        '''
        Initialize GL
        '''
        global mod

        #stuff used as defaults for storing user settings.
        #Removed that feature since I'm lazy and didn't want to import too much from my other projects.
        self.fieldtemp = ["GL_COMPRESSED_RG_RGTC2", 4.0, "GL_LINEAR", "GL_LINEAR", "GL_LINEAR_MIPMAP_LINEAR", "On", "On", "Magic"]

        #mipmap support and NPOT texture support block
        if not hasGLExtension("GL_ARB_framebuffer_object"):
            print "GL_ARB_framebuffer_object not supported, switching to GL_GENERATE_MIPMAP"
            self.npot = 2
        version = glGetString(GL_VERSION)
        if int(version[0]) == 1 and int(version[2]) < 4: #no opengl 1.4 support
            print "GL_GENERATE_MIPMAP not supported, not using mipmapping"
            self.npot = 1
        if not hasGLExtension("GL_ARB_texture_non_power_of_two"):
            print "GL_ARB_texture_non_power_of_two not supported, switching to GL_ARB_texture_rectangle"
            self.texext = GL_TEXTURE_RECTANGLE_ARB
            self.npot = 1
        if not hasGLExtension("GL_ARB_texture_rectangle"):
            print "GL_TEXTURE_RECTANGLE_ARB not supported, switching to GL_TEXTURE_2D"
            self.texext = GL_TEXTURE_2D
            self.npot = 0

        #assorted settings block
        if hasGLExtension("GL_EXT_texture_compression_rgtc") and self.fieldtemp[0] != "None":
            self.compress = self.interpretString(self.fieldtemp[0]) #
            print "using " + self.fieldtemp[0] + " texture compression"
        if hasGLExtension("GL_EXT_texture_filter_anisotropic") and self.fieldtemp[1] > 1.0:
            self.anifilt = self.fieldtemp[1]
            print "using " + str(self.fieldtemp[1]) + "x anisotropic texture filtering. max: " + str(glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT))
        self.minfilter = self.interpretString(self.fieldtemp[2])
        self.magfilter = self.interpretString(self.fieldtemp[3])
        self.mipminfilter = self.interpretString(self.fieldtemp[4])
        if self.mipminfilter == "Off":
            self.mipminfilter = -1
        if self.format().sampleBuffers() and self.fieldtemp[5] == "On":
            print "enabling "  + str(self.format().samples()) + "x FSAA"
            glEnable(GL_MULTISAMPLE)
        else:
            print "FSAA not supported and/or disabled"

        glEnable(self.texext)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glViewport(0, 0, self.width(), self.height())
        glClearColor(0.0, 0.0, 0.0, 0.0)

        initok = False
        if mod:
            ret = glmod.init(self.texext)
            if ret == -1:
                print "Something terrible went wrong in initializing glmod"
                mod = False
            elif ret == -2:
                if self.fieldtemp[6] == "On":
                    print "using gl module, VBO support requested but not available"
                else:
                    print "using gl module, VBO support not requested"
            else:
                initok = True
                if self.fieldtemp[6] == "On":
                    print "using gl module, VBO support requested and available"
                else:
                    print "using gl module, VBO support not requested"

        if mod and initok and self.fieldtemp[6] == "On":
            if glInitVertexBufferObjectARB() and bool(glBindBufferARB):
                self.vbos = True
                print "VBO support initialised succesfully"
                self.VBO = int(glGenBuffersARB(1))
                glmod.initVBO(self.VBO, ADT.arrayByteCount(numpy.zeros((2, 2), 'f')))
            else:
                print "VBO support initialisation failed, continuing without"

    #util functions
    def createImage(self, qimagepath, layer, textureRect, drawRect, hidden = False, dynamicity = GL_STATIC_DRAW_ARB):
        '''
        Creates an rggTile instance, uploads the correct image to GPU if not in cache, and some other helpful things.
        '''
        #print "requested to create", qimagepath, layer, textureRect, drawRect, hidden
        layer = int(layer)
        texture = None
        found = False

        if qimagepath in self.qimages:
            qimg = self.qimages[qimagepath][0]
            if self.qimages[qimagepath][2] > 0:
                texture = self.qimages[qimagepath][1]
                found = True
        else:
            qimg = QImage(qimagepath)
            print "created", qimagepath

        if textureRect[2] == -1:
            textureRect[2] = qimg.width() - 1

        if textureRect[3] == -1:
            textureRect[3] = qimg.height() - 1

        if drawRect[2] == -1:
            drawRect[2] = qimg.width()

        if drawRect[3] == -1:
            drawRect[3] = qimg.height()

        image = Image(qimagepath, qimg, textureRect, drawRect, layer, hidden, dynamicity, self)

        if found == False:
            if self.npot == 0:
                w = nextPowerOfTwo(qimg.width())
                h = nextPowerOfTwo(qimg.height())
                if w != qimg.width() or h != qimg.height():
                    qimg = qimg.scaled(w, h)
     
            img = self.convertToGLFormat(qimg)
            texture = int(glGenTextures(1))
            try:
                imgdata = img.bits().asstring(img.numBytes())
            except:
                import sys
                print "requested to create", qimagepath, layer, textureRect, drawRect, hidden
                for x in [0, 1, 2, 3]:
                    f_code = sys._getframe(x).f_code #really bad hack to get the filename and number
                    print "Doing it wrong in " + f_code.co_filename + ":" + str(f_code.co_firstlineno)
            
            print "created texture", texture

            glBindTexture(self.texext, texture)

            if self.anifilt > 1.0:
                glTexParameterf(self.texext, GL_TEXTURE_MAX_ANISOTROPY_EXT, self.anifilt)
            if self.npot == 3 and self.mipminfilter != -1:
                glTexParameteri(self.texext, GL_TEXTURE_MIN_FILTER, self.mipminfilter)
                glTexParameteri(self.texext, GL_TEXTURE_MAG_FILTER, self.magfilter)
            elif self.npot == 2 and self.mipminfilter != -1:
                glTexParameteri(self.texext, GL_TEXTURE_MIN_FILTER, self.mipminfilter)
                glTexParameteri(self.texext, GL_TEXTURE_MAG_FILTER, self.magfilter)
                glTexParameteri(self.texext, GL_GENERATE_MIPMAP, GL_TRUE)
            else:
                glTexParameteri(self.texext, GL_TEXTURE_MIN_FILTER, self.minfilter)
                glTexParameteri(self.texext, GL_TEXTURE_MAG_FILTER, self.magfilter)

            format = GL_RGBA
            if self.compress:
                format = self.compress

            glTexImage2D(self.texext, 0, GL_RGBA, img.width(), img.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, imgdata);

            if self.npot == 3 and self.mipminfilter != -1:
                glEnable(GL_TEXTURE_2D)
                glGenerateMipmap(GL_TEXTURE_2D)
            
            self.qimages[qimagepath] = [qimg, texture, 1] #texture, reference count
        else:
            self.qimages[qimagepath][2] += 1

        image.textureId = texture

        if layer not in self.images:
            self.images[layer] = []
            self.layers = self.images.keys()
            self.layers.sort()
            image.createLayer = True

        self.images[layer].append(image)

        if self.vbos:
            image.VBO = self.VBO
            if not self.fillBuffers(image):
                self.calculateVBOList(image)

        return image

    def reserveVBOSize(self, size):
        '''
        Reserves a VBO with the specified size as the amount of VBO entries, and re-assigns all images with the new data.
        '''
        if self.vbos and size > self.VBOBuffer:
            self.VBOBuffer = nextPowerOfTwo(size+1)
            print "reserving size", self.VBOBuffer

            self.fillBuffers(None, False) #Automatically does a calculateVBOList()

    def fillBuffers(self, image = None, resize = True):
        '''
        if image == None, this function requests a new BO from the GPU with a calculated size
        if image != None, this function adds the VBO data from image to the BO in the GPU, if there is enough space.
        '''
        size = 0

        for layer in self.layers:
            size += len(self.images[layer])

        glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.VBO)
        
        #print self.offset, (self.VBOBuffer*self.vertByteCount)

        if self.VBOBuffer <= size or image == None or self.offset + self.vertByteCount >= self.VBOBuffer*self.vertByteCount:
            if resize and self.VBOBuffer <= size:
                print "resizing from", size, "to", nextPowerOfTwo(size+1)
                self.VBOBuffer = nextPowerOfTwo(size+1)

            glBufferDataARB(GL_ARRAY_BUFFER_ARB, self.VBOBuffer*self.vertByteCount, None, GL_STATIC_DRAW_ARB)

            self.offset = 0

            for layer in self.layers:
                for img in self.images[layer]:
                    img.offset = int(float(self.offset)/self.vertByteCount*4)
                    VBOData = img.getVBOData()

                    glBufferSubDataARB(GL_ARRAY_BUFFER_ARB, self.offset, self.vertByteCount, VBOData)
                    self.offset += self.vertByteCount
            
            self.calculateVBOList()
            
            glBindBuffer(GL_ARRAY_BUFFER_ARB, 0)
            return True

        else:
            image.offset = int(float(self.offset)/self.vertByteCount*4)
            VBOData = image.getVBOData()

            glBufferSubDataARB(GL_ARRAY_BUFFER_ARB, self.offset, self.vertByteCount, VBOData)
            self.offset += self.vertByteCount

            glBindBuffer(GL_ARRAY_BUFFER_ARB, 0)
            return False

    def deleteImage(self, image):
        '''
        Decreases the reference count of the texture by one, and deletes it if nothing is using it anymore
        '''

        self.qimages[image.imagepath][2] -= 1

        if self.qimages[image.imagepath][2] <= 0:
            print "deleting texture", image.textureId
            glDeleteTextures(image.textureId)
            del self.qimages[image.imagepath]

        self.images[image.layer].remove(image)

        if self.vbos:
            self.calculateVBOList(image, True)

        image = None

    def deleteImages(self, imageArray):
        '''
        Decreases the reference count of the texture of each image by one, and deletes it if nothing is using it anymore
        '''

        for image in imageArray:
            self.qimages[image.imagepath][2] -= 1

            if self.qimages[image.imagepath][2] <= 0:
                print "deleting texture", image.textureId
                glDeleteTextures(image.textureId)
                del self.qimages[image.imagepath]

            self.images[image.layer].remove(image)

        if self.vbos:
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
        
    def calculateVBOList(self, image = None, delete = False):
        '''
        Create the VBO list to be passed on to the module for drawing
        or if the change is only one image, modify it.
        '''
        if len(self.layers) > 0 and image != None:
            if delete:
                #print "delete"
                temp = [self.layers.index(image.layer)]
                for img in self.images[image.layer]:
                    if img.hidden or img == image:
                        continue
                    temp.append(int(img.textureId))
                    temp.append(img.offset)
                glmod.setVBOlayer(tuple(temp))
            elif image.createLayer:
                layer = self.layers.index(image.layer)
                glmod.insertVBOlayer((layer, int(image.textureId), image.offset))
                #print "addLayer", (layer, image.textureId, image.offset)
                image.createLayer = False
            else:
                layer = self.layers.index(image.layer)
                #print "addEntry", (layer, image.textureId, image.offset)
                glmod.addVBOentry((layer, int(image.textureId), image.offset))
            return

        vbolist = []
        for layer in self.layers:
            temp = []
            for img in self.images[layer]:
                if img.hidden:
                    continue
                temp.append(img.textureId)
                temp.append(img.offset)
            vbolist.append(tuple(temp))

        if len(vbolist) > 0:
            #print "setVBO", vbolist
            glmod.setVBO(tuple(vbolist))

    def hideImage(self, image, hide):
        '''
        This function should only be called from image.py
        Use Image.hide() instead.
        '''
        if self.vbos:
            self.calculateVBOList(image, hide)
            
    def setLayer(self, image, newLayer):
        '''
        This function should only be called from image.py
        Use Image.layer instead.
        '''
        if self.vbos:
            self.calculateVBOList(image, True)

        oldLayer = image._layer
        image._layer = newLayer
        if newLayer not in self.images:
            self.images[newLayer] = []
            self.layers = self.images.keys()
            self.layers.sort()
            image.createLayer = True

        self.images[oldLayer].remove(image)
        self.images[newLayer].append(image)

        if self.vbos:
            self.calculateVBOList(image)
            
    def getImageSize(self, image):
    
        qimg = None
        if image in self.qimages:
            qimg = self.qimages[image][0]
        else:
            qimg = QImage(image)
        
        return qimg.size()
        
    def addText(self, text, pos):
        self.texts.append([self.textid, text, pos])
        self.textid += 1
        return self.textid - 1
        
    def removeText(self, id):
        for i, t in enumerate(self.texts):
            if t[0] == id:
                self.texts.pop(i)
                return
            
    def setTextPos(self, id, pos):
        for t in self.texts:
            if t[0] == id:
                t[2] = pos

    def mouseMoveEvent(self, mouse):
        if self.movecam:
            newx = self.camera[0] + mouse.pos().x() - self.lastMousePos[0]
            newy = self.camera[1] + mouse.pos().y() - self.lastMousePos[1]
            
            self.camera[0] = newx
            self.camera[1] = newy

            if newx < Globals.rightBound * self.zoom + self.w:
                self.camera[0] = Globals.rightBound * self.zoom + self.w
            elif newx > Globals.leftBound:
                self.camera[0] = Globals.leftBound
            if newy > Globals.upBound:
                self.camera[1] = Globals.upBound
            elif newy < Globals.downBound * self.zoom + self.h:
                self.camera[1] = Globals.downBound * self.zoom + self.h
        
        self.lastMousePos = [mouse.pos().x(), mouse.pos().y()]
        self.mouseMove.emit(mouse.pos().x(), mouse.pos().y())

        mouse.accept()

    def mousePressEvent(self, mouse):
        self.lastMousePos = (mouse.pos().x(), mouse.pos().y())

        button = -1

        if mouse.button() == Qt.LeftButton:
            button = 1
        elif mouse.button() == Qt.RightButton:
            button = 2
            self.movecam = True
        elif mouse.button() == Qt.MidButton:
            button = 3
        self.mousePress.emit(button, (mouse.pos().x()-self.camera[0])/self.zoom, (mouse.pos().y()-self.camera[1])/self.zoom)

        mouse.accept()
        
    def mouseReleaseEvent(self, mouse):
        if mouse.button() == Qt.RightButton:
            self.movecam = False

        mouse.accept()

    def wheelEvent(self, mouse):
        oldCoord = [mouse.pos().x(), mouse.pos().y()]
        oldCoord[0] *= float(1)/self.zoom
        oldCoord[1] *= float(1)/self.zoom

        oldCoord2 = self.camera
        oldCoord2[0] *= float(1)/self.zoom
        oldCoord2[1] *= float(1)/self.zoom

        # Change zoom level
        if mouse.delta() < 0 and self.zoom > 0.55:
            self.zoom -= 0.15
        elif mouse.delta() > 0 and self.zoom < 1.59:
            self.zoom += 0.15

        self.camera[0] = oldCoord2[0] * self.zoom - ((oldCoord[0]*self.zoom)-mouse.pos().x())
        self.camera[1] = oldCoord2[1] * self.zoom - ((oldCoord[1]*self.zoom)-mouse.pos().y())
        
        # zoom near edges limits view to bounds to prevent zooming into black
        if Globals.rightBound*self.zoom + self.w > self.camera[0]:
            self.camera[0] = Globals.rightBound * self.zoom + self.w
        elif Globals.leftBound * self.zoom < self.camera[0]:
            self.camera[0] = Globals.leftBound * self.zoom
        
        if Globals.downBound * self.zoom + self.h > self.camera[1]:
            self.camera[1] = Globals.downBound * self.zoom + self.h
        elif Globals.upBound * self.zoom < self.camera[1]:
            self.camera[1] = Globals.upBound * self.zoom
        mouse.accept()
        
    def leaveEvent(self, event):
        self.movecam = False
