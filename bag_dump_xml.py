#!/usr/bin/env python
from __future__ import print_function

__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
Dump the xml for a bag.


@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 28-May-2010

@requires: U{Python<http://python.org/>} >= 2.6
@requires: U{lxml<http://codespeak.net/lxml/>}
@requires: U{h5py<http://code.google.com/p/h5py/>}
'''

import sys,os
from StringIO import StringIO
#from lxml import etree 
import h5py

import sqlite3

f = h5py.File(sys.argv[1])

bag_root = f['/BAG_root']
metadata_xml = ''.join(bag_root['metadata'])

# metadata_txt = etree.tostring(root, pretty_print=True ).replace('</',' ').replace('<',' ').replace('>',' ') #.replace('\n','<br/>\n')

o = open(sys.argv[1]+'.xml','w')
o.write(metadata_xml)
