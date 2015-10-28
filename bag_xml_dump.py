#!/usr/bin/env python
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2008'
__license__   = 'Apache 2.0'
__contact__   = 'schwehr@gmail.com'

__doc__='''
Create a bounding box and thumb tack for a Bathymetric Attributed Grid (BAG)

@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 12-May-2009

@requires: U{Python<http://python.org/>} >= 2.6
@requires: U{lxml<http://codespeak.net/lxml/>}
@requires: U{h5py<http://code.google.com/p/h5py/>}
'''
import sys,os
from StringIO import StringIO
from lxml import etree
import h5py

# FIX: make this a proper script

import sys

def dump_metadata(bag,out):
    f = h5py.File(bag)
    bag_root = f['/BAG_root']
    metadata_xml = ''.join(bag_root['metadata'])
    #o = file(sys.argv[1]+'.xml','w') #sys.argv[2],'w')
    out.write(metadata_xml)

def get_parser():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-b','--bag',
                      help= 'Bag file to get the metadata from')
    parser.add_option('-o','--output-xml',
                      help= 'Where to write the xml metadata  [default: stdout]')
    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    return parser

if __name__ == '__main__':
    
    (options, args) = get_parser().parse_args()

    out = sys.stderr
    if options.output_xml is not None:
        out = file(options.output_xml,'w')

    dump_metadata(options.bag, out)

