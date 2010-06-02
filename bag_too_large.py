#!/usr/bin/env python
from __future__ import print_function
# Since: 02-June-2010

import osgeo.gdal
import osgeo.gdal as gdal
import osgeo.gdalconst

import sys

def bag_too_large(filename, max_dim_size):
    src = osgeo.gdal.Open(filename, osgeo.gdal.GA_ReadOnly)
    w,h = src.RasterXSize,src.RasterYSize
    if w > max_dim_size or h > max_dim_size: return True

    return False

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] ...",)
                          #version="%prog "+__version__+' ('+__date__+')')
    
    parser.add_option('-f', '--filename', help='file to check.  Anything that gdal reads')
    parser.add_option('-m', '--max-cells', type='int', default=10000,
                      help='[default: %default]"')
    parser.add_option('-v', '--verbose', default=False, action='store_true',
                      help='run in verbose mode')
    (options, args) = parser.parse_args()
    v = options.verbose

    if options.filename is None:
        print ('ERROR: must specify input file')
        return False

    if bag_too_large(options.filename, options.max_cells):
        if v: print ('bag too large')
        sys.exit(1)


if __name__ == '__main__':
    osgeo.gdal.AllRegister()
    main()
