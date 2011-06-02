#!/usr/bin/env python

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

import sys
sys.path.insert(0, '..')

from const.constants import *

class InvalidMap(Exception): pass

def is_walkable(x, y, nr, nc, m):
    """Return whether the given coordinate resides inside the map
    and its status is NORMAL.
    """
    return x >= 0 and x < nc and \
           y >= 0 and y < nr and \
           m[y][x] != BLOCKED

def make_graph(s): 
    """
    Generate an adjacency-list-represented graph from a multi-line string.
    
    :Parameters:
        s : str
            A multi-line string representing the maze. 
            A sample string is as follows:
            s = '''
                1001
                0100
                1001
                '''
        
    :Return:
        graph : {(x1, y1): {(x2, y2): dist, ... }, ... }
            The graph is in ajacency list representation.
            The graph generated using the sample input above is as follows:
            graph = {(0, 1): {},
                     (1, 2): {(2, 1): 14, (2, 2): 10}, 
                     (3, 1): {(2, 0): 14, (2, 1): 10, (2, 2): 14}, 
                     (2, 1): {(1, 2): 14, (2, 0): 10, (1, 0): 14, (3, 1): 10, (2, 2): 10}, 
                     (2, 0): {(1, 0): 10, (3, 1): 14, (2, 1): 10}, 
                     (2, 2): {(1, 2): 10, (3, 1): 14, (2, 1): 10}, 
                     (1, 0): {(2, 0): 10, (2, 1): 14}}

        source : (x, y)
            source coordinate

        target : (x, y)
            target coordinate

    """
    try:
        nodes_map = [list(row) for row in s.split()]
        n_row = len(nodes_map)
        n_col = len(nodes_map[0])
    except:
        raise InvalidMap("The given raw map may be invalid")

    # put all available nodes into the graph
    g = dict([((x, y), {})  
            for x in xrange(n_col) 
                for y in xrange(n_row)
                    if nodes_map[y][x] != BLOCKED]) 
    source = None
    target = None

    for x in xrange(n_col):
        for y in xrange(n_row):
            if nodes_map[y][x] == SOURCE:
                source = (x, y)
            elif nodes_map[y][x] == TARGET:
                target = (x, y)
            if is_walkable(x, y, n_row, n_col, nodes_map):
                for i in xrange(len(XOFFSET)):
                    # inspect horizontal and vertical adjacent nodes
                    nx = x + XOFFSET[i]
                    ny = y + YOFFSET[i]
                    if is_walkable(nx, ny, n_row, n_col, nodes_map):
                        g[(x, y)][(nx, ny)] = DIST
                        # further inspect diagonal nodes
                        nx = x + DAXOFFSET[i]
                        ny = y + DAYOFFSET[i]
                        if is_walkable(nx, ny, n_row, n_col, nodes_map):
                            g[(x, y)][(nx, ny)] = DDIST
                        nx = x + DBXOFFSET[i]
                        ny = y + DBYOFFSET[i]
                        if is_walkable(nx, ny, n_row, n_col, nodes_map):
                            g[(x, y)][(nx, ny)] = DDIST
    return g, source, target



if __name__ == '__main__':
    nodes_map_raw = '''
                    1S01
                    0100
                    1T01
                    '''
    print make_graph(nodes_map_raw) 
