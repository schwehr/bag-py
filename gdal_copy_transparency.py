#!/usr/bin/env python
from __future__ import print_function
__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2010'
__license__   = 'GPL v3'
__contact__   = 'kurt at ccom.unh.edu'

__doc__='''
Use the gdal python interface to combine the hillshade
with proper transparency.

@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 01-June-2010

@requires: U{Python<http://python.org/>} >= 2.6
@requires: U{gdal<http://gdal.org/>} >= 1.7
'''

import osgeo.gdal
import osgeo.gdal as gdal
import osgeo.gdalconst

import sys


def transparent_image(color_relief_name, hillshade_name, outfile_name, verbose = False):
    v = verbose
    hillshade = osgeo.gdal.Open(hillshade_name, osgeo.gdal.GA_ReadOnly)
    color = osgeo.gdal.Open(color_relief_name, osgeo.gdal.GA_ReadOnly)

    w1,h1 = color.RasterXSize,color.RasterYSize
    w2,h2 = hillshade.RasterXSize,hillshade.RasterYSize
    if v: print ('dim: color:',w1,h1,'\t\thillshade:',w2,h2)
    if w1 != w2 or h1 != h2:
        print('ERROR: width and height must be the same.  Found (',w1,h1,') and (',w2,h2,')')
        return False

    driver = gdal.GetDriverByName('GTiff')
    if driver is None:
        print('ERROR: Format driver %s not found, pick a supported driver.' % format)
        return False

    dst = driver.CreateCopy(outfile_name, color) #, 0) # 0 For GeoTiff

    if v:
        print ('gdal.GCI_AlphaBand:',gdal.GCI_AlphaBand)
        for band_num in range(1,color.RasterCount+1):
            band = color.GetRasterBand(band_num)
            if band is None:
                print ('band is None')
                continue
            bandmin,bandmax = band.ComputeRasterMinMax()
            clr_interp = band.GetColorInterpretation()
            print ('color_band_info:', band_num, bandmin,bandmax, clr_interp, gdal.GetColorInterpretationName(clr_interp))

    alpha = color.GetRasterBand(4)
    gray_band = hillshade.GetRasterBand(1)

    # Shove all the same gray values into all the color channels
    for band_num in range(1,4):
        dst.GetRasterBand(band_num).WriteArray(gray_band.ReadAsArray())

    # Set the alpha
    dst.GetRasterBand(4).WriteArray(alpha.ReadAsArray())

    return True

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] ...",
                          version="%prog "+__version__+' ('+__date__+')')
    
    parser.add_option('-c', '--color-relief', help='')
    parser.add_option('-H', '--hillshade', help='gdaldem hillshade geotiff')
    parser.add_option('-o', '--outfile', help='The resulting file to create.  '
                      + '[default: hillshade+"-alpha.tif"')
    parser.add_option('-v', '--verbose', default=False, action='store_true', help='run the tests run in verbose mode')
    (options, args) = parser.parse_args()
    v = options.verbose

    if options.color_relief is None or options.hillshade is None:
        print ('ERROR: must specify both color-relief and hillshade input files')
        return False

    if options.outfile is None:
        options.outfile = options.hillshade + '-alpha.tif'
    print (options)
    transparent_image(options.color_relief, options.hillshade, options.outfile, v)

if __name__ == '__main__':
    osgeo.gdal.AllRegister()
    #print ('hello')
    main()

