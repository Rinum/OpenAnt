# Copyright (C) 2011 by Xueqiao Xu <xueqiaoxu@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# =======================================
# used by path finding
# =======================================
XOFFSET   = (0, 1, 0, -1)
YOFFSET   = (-1, 0, 1, 0)
DAXOFFSET = (1, 1, -1, -1)
DAYOFFSET = (-1, 1, 1, -1)
DBXOFFSET = (-1, 1, 1, -1) 
DBYOFFSET = (-1, -1, 1, 1)

NORMAL  = '0'
BLOCKED = '1'
SOURCE  = 'S'
TARGET  = 'T'

OPENED = 'P'
CLOSED = 'C'

SCALE = 10
DIST  = 10
DDIST = 14 # diagonal distance
INF   = int(1e9)

MANHATTAN = 0
EUCLIDEAN = 1
CHEBYSHEV = 2

ASTARM   = 0
ASTARE   = 1
ASTARC   = 2
DIJKSTRA = 3
BDBFS    = 4

OSOURCE = 1
OTARGET = 2
CSOURCE = 1
CTARGET = 2

# =======================================
# used by C/S communication
# =======================================
TERM = '<end>' # line terminator
RUNNING = 0
STOPPED = 1



# =======================================
# used by GUI
# =======================================
CAPTION = 'Path Finding 0.1.1'

NODE_SIZE  = 35
RESOLUTION = (910, 700)
MAP_SIZE = (910, 700)

FPS_LIMIT  = 30

FONT_NAME = 'freesansbold.ttf'

ICON_NAME = 'ico.png'

# speed settings
DEFAULT_SPEED = 128
SPEED_MAX = 4096

# countdown settings
COUNTDOWN_COOLDOWN = 5

# color table
BACKGROUND_COLOR         = 'gray95'
GRID_LINE_COLOR          = 'gray'
NORMAL_COLOR             = 'white'
BLOCKED_COLOR            = 'gray50'
OPENED_COLOR             = 'palegreen'
CLOSED_COLOR             = 'paleturquoise'
SOURCE_COLOR             = 'green2'
TARGET_COLOR             = 'tomato1'
PARENT_LINE_COLOR        = 'gray'
NODE_INFO_COLOR          = 'gray30'
CONTROL_FONT_COLOR       = 'white'
SELECTED_COLOR           = 'tomato1'
HELP_FONT_COLOR          = 'white'
PATH_COLOR               = 'yellow1'
SPEED_FONT_COLOR         = 'white'
CONNECTION_FAILURE_COLOR = 'tomato1'
CONNECTION_SUCCESS_COLOR = 'white'

PATH_WIDTH = 3 # path line width

NODE_INFO_FONT_SIZE = 8
MARGIN = 3

# control info
CONTROL_FONT_SIZE = 11
CONTROL_POS = (790, 5)
CONTROL_TEXT_POS = (795, 10)
CONTROL_Y_OFFSET = 16


# help info
HELP_FONT_SIZE = 11
HELP_POS = (5, 5)
HELP_TEXT_POS = (10, 10)
HELP_Y_OFFSET = 16

# connection info
CONNECTION_FAILURE_FONT_SIZE = 30
CONNECTION_FAILURE_Y = 270

CONNECTION_COUNTDOWN_FONT_SIZE = 30
CONNECTION_COUNTDOWN_Y = 320

CONNECTION_SUCCESS_POS = (5, 680)
CONNECTION_SUCCESS_FONT_SIZE = 12
CONNECTION_SUCCESS_TEXT_POS = (10, 683)

# gui status
DRAWING   = 0
RECEIVING = 1
EXIT      = 2
