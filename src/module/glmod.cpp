/*
 * Module for use in Oipo's Graphics Engine 2.0
 *
 * By Oipo (kingoipo@gmail.com)
 */

#include <Python.h>
#include <vector>
#include <ext/hash_map>

#define GL_GLEXT_PROTOTYPES 1

#ifdef __APPLE__
    #include <OpenGL/gl.h>
#else
    #ifdef _WIN32
        #undef GL_GLEXT_PROTOTYPES
        #include <GL/gl.h>
        #define WIN32_LEAN_AND_MEAN 1
        #include <windows.h>
        #include "glext.h"
        PFNGLBINDBUFFERPROC glBindBuffer = NULL;
        PFNGLMULTIDRAWARRAYSPROC glMultiDrawArrays = NULL;
    #else
        #include <GL/gl.h>
    #endif
#endif

#ifdef DEBUG
    #warning "DEBUG ENABLED, EXPECT PERFORMANCE LOSS"
    #define PyTuple_GETITEM(a,b) PyTuple_GetItem(a,b)
    #define PyList_GETITEM(a,b) PyList_GetItem(a,b)
    #define PyInt_ASLONG(a) PyInt_AsLong(a)
    #define PyLong_ASLONG(a) PyLong_AsLong(a)
    #define PyFloat_ASDOUBLE(a) PyFloat_AsDouble(a)
#else
    #define PyTuple_GETITEM(a,b) PyTuple_GET_ITEM(a,b)
    #define PyList_GETITEM(a,b) PyList_GET_ITEM(a,b)
    #define PyInt_ASLONG(a) PyInt_AS_LONG(a)
    #define PyFloat_ASDOUBLE(a) PyFloat_AS_DOUBLE(a)
    #define PyLong_ASLONG(a) PyLong_AsLong(a) //there is no alternative to this function

#endif

#define BUFFER_OFFSET(i) ((char *)NULL + (i))

using namespace std;
using namespace __gnu_cxx;

GLenum extension = GL_TEXTURE_RECTANGLE_ARB;

class VBOEntry
{
    public:
    unsigned int texid;
    vector<GLint> offsetValues;

    VBOEntry()
    {
        this->texid = 0;
    }

    VBOEntry(unsigned int texid, unsigned int offset)
    {
        this->texid = texid;
        offsetValues.push_back(offset);
    }

    void addOffset(unsigned int offset)
    {
        offsetValues.push_back(offset);
    }
};

typedef hash_map<unsigned int, VBOEntry> dict;

int VBO, stride, valuesSize = -1;
vector<dict> entries;
GLint *firstValues;
GLsizei *countValues;

void resizeValues(int newSize)
{
    if(newSize <= valuesSize)
        return;

    if(valuesSize > 0)
    {
        delete[] firstValues;
        delete[] countValues;
    }

    firstValues = new GLint[newSize];
    countValues = new GLsizei[newSize];

    for(int j = 0; j < newSize; j++)
    {
        countValues[j] = 4;
    }

    valuesSize = newSize;
}

static PyObject * glmod_drawTexture(PyObject *self, PyObject* args)
{
    int texid, ok;
    float x, y, w, h, cx, cy, cw, ch;

    ok = PyArg_ParseTuple(args, "iffffffff", &texid, &x, &y, &w, &h, &cx, &cy, &cw, &ch);

    if(!ok)
       return PyInt_FromLong(-1L); 

    glBindTexture(extension, texid);

    glBegin(GL_QUADS);
    //Top-left vertex (corner)
    glTexCoord2f(cx, cy+ch); //image/texture
    glVertex3f(x, y, 0); //_screen coordinates

    //Bottom-left vertex (corner)
    glTexCoord2f(cx+cw, cy+ch);
    glVertex3f(x+w, y, 0);

    //Bottom-right vertex (corner)
    glTexCoord2f(cx+cw, cy);
    glVertex3f(x+w, y+h, 0);

    //Top-right vertex (corner)
    glTexCoord2f(cx, cy);
    glVertex3f(x, y+h, 0);
    glEnd();

    return PyInt_FromLong(0L);
}

static PyObject * glmod_drawVBO(PyObject *self, PyObject* args)
{
    int i, j, k, x, lastid = -1;
    

    glBindBuffer(GL_ARRAY_BUFFER_ARB, VBO);
    glTexCoordPointer(2, GL_FLOAT, stride, 0);
    glVertexPointer(2, GL_FLOAT, stride, BUFFER_OFFSET(stride/2));

    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_TEXTURE_COORD_ARRAY);

    for(i = 0; i < entries.size(); i++)
    {
        dict::iterator it = entries[i].begin();
        while(it != entries[i].end())
        {
            VBOEntry* e = &((*it).second);
            k = e->offsetValues.size();
            glBindTexture(extension, e->texid);

            for(int j = 0; j < k; j++)
                firstValues[j] = e->offsetValues[j];

            glMultiDrawArrays(GL_QUADS, firstValues, countValues, k);
            it++;
        }
    }

    glDisableClientState(GL_VERTEX_ARRAY);
    glDisableClientState(GL_TEXTURE_COORD_ARRAY);
    glBindBuffer(GL_ARRAY_BUFFER_ARB, 0);

    return PyInt_FromLong(0L);
}

static PyObject * glmod_setVBO(PyObject *self, PyObject* args)
{
    PyObject *tuple = PyTuple_GETITEM(args, 0);
    int i, j;
    unsigned int texid, offset;
    PyObject *layer= NULL;
    
    entries.clear();

    for(i = 0; i < PyTuple_Size(tuple); i++)
    {
        entries.push_back(dict());
        layer = PyTuple_GETITEM(tuple, i);
        for(j = 0; j < PyTuple_Size(layer); j += 2)
        {
            texid = PyInt_ASLONG(PyTuple_GETITEM(layer, j));
            offset = PyInt_ASLONG(PyTuple_GETITEM(layer, j+1));
            
            dict::iterator it = entries[i].find(texid);
            if(it == entries[i].end())
                entries[i][texid] = VBOEntry(texid, offset);
            else
            {
                entries[i][texid].addOffset(offset);
                if(entries[i][texid].offsetValues.size() >= valuesSize)
                    resizeValues(entries[i][texid].offsetValues.size() + 5);
            }
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_insertVBOlayer(PyObject *self, PyObject* args)
{
    PyObject *tuple = PyTuple_GETITEM(args, 0);
    int j;
    unsigned int texid, offset, insertBeforeLayer;

    insertBeforeLayer = PyInt_ASLONG(PyTuple_GETITEM(tuple, 0));
    
    if(insertBeforeLayer >= entries.size())
        entries.push_back(dict());
    else
        entries.insert(entries.begin() + insertBeforeLayer, dict());

    for(j = 1; j < PyTuple_Size(tuple); j += 2)
    {
        texid = PyInt_ASLONG(PyTuple_GETITEM(tuple, j));
        offset = PyInt_ASLONG(PyTuple_GETITEM(tuple, j+1));
        //printf("adding %i at %i on %i\r\n", texid, offset, insertBeforeLayer);
        
        dict::iterator it = entries[insertBeforeLayer].find(texid);
        if(it == entries[insertBeforeLayer].end())
            entries[insertBeforeLayer][texid] = VBOEntry(texid, offset);
        else
        {
            entries[insertBeforeLayer][texid].addOffset(offset);
            if(entries[insertBeforeLayer][texid].offsetValues.size() >= valuesSize)
                resizeValues(entries[insertBeforeLayer][texid].offsetValues.size() + 5);
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_setVBOlayer(PyObject *self, PyObject* args)
{
    PyObject *tuple = PyTuple_GETITEM(args, 0);
    int j;
    unsigned int texid, offset, layer;

    layer = PyInt_ASLONG(PyTuple_GETITEM(tuple, 0));
#ifdef DEBUG
    if(layer > entries.size())
    {
        printf("SetLayer Layer too high\r\n");
        return PyInt_FromLong(-1L);
    }
#endif
    entries[layer].clear();

    for(j = 1; j < PyTuple_Size(tuple); j += 2)
    {
        texid = PyInt_ASLONG(PyTuple_GETITEM(tuple, j));
        offset = PyInt_ASLONG(PyTuple_GETITEM(tuple, j+1));
        
        dict::iterator it = entries[layer].find(texid);
        if(it == entries[layer].end())
            entries[layer][texid] = VBOEntry(texid, offset);
        else
        {
            entries[layer][texid].addOffset(offset);
            if(entries[layer][texid].offsetValues.size() >= valuesSize)
                resizeValues(entries[layer][texid].offsetValues.size() + 5);
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_addVBOentry(PyObject *self, PyObject* args)
{
    PyObject *tuple = PyTuple_GETITEM(args, 0);
    int j;
    unsigned int texid, offset, layer;

    layer = PyInt_ASLONG(PyTuple_GETITEM(tuple, 0));
#ifdef DEBUG
    if(layer > entries.size())
    {
        printf("AddEntry Layer too high\r\n");
        return PyInt_FromLong(-1L);
    }
#endif
    for(j = 1; j < PyTuple_Size(tuple); j += 2)
    {
        texid = PyInt_ASLONG(PyTuple_GETITEM(tuple, j));
        offset = PyInt_ASLONG(PyTuple_GETITEM(tuple, j+1));
        
        dict::iterator it = entries[layer].find(texid);
        if(it == entries[layer].end())
            entries[layer][texid] = VBOEntry(texid, offset);
        else
        {
            entries[layer][texid].addOffset(offset);
            if(entries[layer][texid].offsetValues.size() >= valuesSize)
                resizeValues(entries[layer][texid].offsetValues.size() + 5);
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_drawSelectionCircles(PyObject *self, PyObject* args)
{
    PyObject *dict = PyTuple_GETITEM(args, 0);
    int i = 0; int r = 0;

    PyObject *key, *values, *value, *test;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict, &pos, &key, &values)) {
        for(i = 0; i < PyList_Size(values); i++) 
        {
            value = PyList_GETITEM(values, i);
            glLineWidth(3);
            glColor3f(0.0, 1.0, 0.0);
            glDisable(extension);
            glBegin(GL_LINE_LOOP);
            double x = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 0));
            double y = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 1));
	        double rad = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 2));
            for (r = 0; r < 360; r = r + 3)
            {
                glVertex2f(x + cos(r*0.01745329) * rad, y + sin(r*0.01745329) * rad);
            }
            glEnd();
            glEnable(extension);
            glColor3f(1.0, 1.0, 1.0);
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_drawRectangles(PyObject *self, PyObject* args)
{
    PyObject *dict = PyTuple_GETITEM(args, 0);
    int i = 0;

    PyObject *key, *values, *value, *test;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict, &pos, &key, &values)) {
        for(i = 0; i < PyList_Size(values); i++) 
        {
            value = PyList_GETITEM(values, i);

            double x = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 0));
            double y = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 1));
            double w = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 2));
            double h = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 3));
            double r = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 4));
            double g = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 5));
            double b = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 6));

            glLineWidth(2);
            glColor3f(r, g, b);
            glDisable(extension);
            glBegin(GL_LINE_LOOP);

            glVertex2d(x, y);
            glVertex2d(w, y);
            glVertex2d(w, h);
            glVertex2d(x, h);

            glEnd();
            glEnable(extension);
            glColor3f(1.0, 1.0, 1.0);
        }
    }

    return PyInt_FromLong(0L);
}

static PyObject * glmod_drawLines(PyObject *self, PyObject* args)
{
    PyObject *dict = PyTuple_GETITEM(args, 0);
    int prevthickness = 0, thickness, i = 0;
    
    PyObject *key, *values, *value, *test;
    Py_ssize_t pos = 0;

    glDisable(extension);

    glBegin(GL_LINES);
    while (PyDict_Next(dict, &pos, &key, &values)) {
        thickness = PyInt_ASLONG(key);
        if(thickness != prevthickness)
        {
            glEnd();
            glLineWidth(thickness);
            prevthickness = thickness;
            glBegin(GL_LINES);
        }
#ifdef DEBUG
        if(!PyList_Check(values))
        {
            printf("values not a list\r\n");
            return PyInt_FromLong(0L);
        }
#endif
        for(i = 0; i < PyList_Size(values); i++)
        {
            value = PyList_GETITEM(values, i);
#ifdef DEBUG
            if(!PyTuple_Check(value))
            {
                printf("value not a tuple\r\n");
                return PyInt_FromLong(0L);
            }
            if(!PyFloat_Check(PyTuple_GETITEM(value, 0)))
            {
                printf("x not a tuple\r\n");
                return PyInt_FromLong(0L);
            }
#endif
            double x = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 0));
            double y = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 1));
            double w = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 2));
            double h = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 3));

            double r = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 4));
            double g = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 5));
            double b = PyFloat_ASDOUBLE(PyTuple_GETITEM(value, 6));

            glColor3f(r, g, b);

            glVertex2d(x, y);
            glVertex2d(w, h);
        }
    }
    glEnd();

    glEnable(extension);
    glColor3f(1.0, 1.0, 1.0);

    return PyInt_FromLong(0L);
}

static PyObject * glmod_initVBO(PyObject *self, PyObject* args)
{
    int ok;
    ok = PyArg_ParseTuple(args, "ii", &VBO, &stride);

    if(!ok)
        return PyInt_FromLong(-1L); //Parse error
    return PyInt_FromLong(0L);
}

static PyObject * glmod_init(PyObject *self, PyObject* args)
{
    int ok;

    ok = PyArg_ParseTuple(args, "i", &extension);

    if(!ok)
        return PyInt_FromLong(-1L); //Parse error

#ifdef _WIN32
    glBindBuffer = (PFNGLBINDBUFFERARBPROC)wglGetProcAddress("glBindBufferARB");
    if(glBindBuffer == NULL)
        return PyInt_FromLong(-2L); //Init went ok, but couldn't get glBindBuffer
    glMultiDrawArrays = (PFNGLMULTIDRAWARRAYSPROC)wglGetProcAddress("glMultiDrawArraysEXT");
    if(glMultiDrawArrays == NULL)
        return PyInt_FromLong(-2L); //Init went ok, but couldn't get glMultiDrawArrays
#endif

    resizeValues(4);

    return PyInt_FromLong(0L);
}

static PyMethodDef GLModMethods[] = {
    {"drawTexture",  glmod_drawTexture, METH_VARARGS, "draw a texture"},
    {"drawVBO",  glmod_drawVBO, METH_VARARGS, "draw the list of texids with VBO"},
    {"setVBO",  glmod_setVBO, METH_VARARGS, "erase & set the list of VBO entries"},
    {"insertVBOlayer",  glmod_insertVBOlayer, METH_VARARGS, "add a layer of VBO entries"},
    {"setVBOlayer",  glmod_setVBOlayer, METH_VARARGS, "erase & set a layer of VBO entries"},
    {"addVBOentry",  glmod_addVBOentry, METH_VARARGS, "add an entry to a layer"},
    {"drawLines",  glmod_drawLines, METH_VARARGS, "draws lines from a dict"},
    {"drawSelectionCircles",  glmod_drawSelectionCircles, METH_VARARGS, "draws selection circles from a dict"},
    {"drawRectangles",  glmod_drawRectangles, METH_VARARGS, "draws rectangles from a dict"},
    {"init",  glmod_init, METH_VARARGS, "init"},
    {"initVBO",  glmod_initVBO, METH_VARARGS, "initVBO"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};


PyMODINIT_FUNC initglmod(void)
{
    PyObject *m;
    PyImport_AddModule("glmod");
    m = Py_InitModule("glmod", GLModMethods);
    if (m == NULL)
        return;
}


