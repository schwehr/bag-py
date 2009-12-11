#!/usr/bin/env python
import sys, os
import osgeo.gdal
import osgeo.gdalconst

import numpy as np
import matplotlib.pyplot as plt

__version__='0.1'
__date__='?'

def get_template_data(survey, basename, urlbase, verbose):

    if urlbase is None:
        urlbase = ''
    elif urlbase[-1] != '/':
        urlbase += '/'
    url = urlbase

    patch_name= basename
    td = {} # template_dict/data
    #td['urlbase'] = 'http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/{survey}/{patch}'.format(survey=survey, patch=patch_name)
    td['survey'] = survey
    td['patch'] = patch_name
    td['bag'] = patch_name + '.bag'
    td['thumb'] = url + patch_name + '-thumb.jpg'
    td['image'] = url + patch_name + '.jpg'
    td['url'] = url #urlbase
    #td['info'] = url +  patch_name + '.info.txt'

    osgeo.gdal.AllRegister()
    print 'patch_name:',patch_name
    bag = osgeo.gdal.Open(patch_name + '.bag')
    assert bag
    gt_bag =  bag.GetGeoTransform()
    td['dx_m'] = '%02.1f' % gt_bag[1]
    td['dy_m'] = '%02.1f' % gt_bag[5]

    w,h = bag.RasterXSize,bag.RasterYSize
    td['w'] = w
    td['h'] = h


    print 'Opening:',patch_name + '.tif'
    patch = osgeo.gdal.Open(patch_name + '.tif')
    if patch is None:
        raise ValueError('Unable to open patch')

    w,h = patch.RasterXSize,patch.RasterYSize
    #td['w'] = w
    #td['h'] = h
    gt =  patch.GetGeoTransform()
    gt_dict = {'ul_x':gt[0], 'x_res':gt[1], 'ul_y':gt[3], 'y_res':gt[5]}
    if verbose:
        print gt_dict

    dx = gt[1]
    x0 = gt[0]
    x1 = x0 + w * dx

    dy = gt[5]
    y1 = gt[3]
    y0 = y1 + h * dy # dy should be negative

    td['dx_deg'] = dx
    td['dy_deg'] = dy

    td['x0'] = '%02.3f' % x0
    td['x1'] = '%02.3f' % x1

    td['y0'] = '%02.3f' % y0
    td['y1'] = '%02.3f' % y1

    td['x_center'] = (x0 + x1) / 2
    td['y_center'] = (y0 + y1) / 2

    td['histogram'] = url + patch_name + '-hist.png'
    td['histogram_thumb'] = url + patch_name + '-hist-thumb.jpg'
    td['cwd'] = os.getcwd()
    td['metadata_xml'] = patch_name + '.metadata.xml'

    return td

def histogram(basename,verbose):
    'Plot the depth histogram.  Use the tif until gdal 1.7.0 comes out'

    patch = osgeo.gdal.Open(basename + '.tif')
    band = patch.GetRasterBand(1)
    bandmin,bandmax = band.ComputeRasterMinMax()
    hist = band.GetDefaultHistogram()

    hist_vals = hist[3][:-1]
    while hist_vals[-1] == 0:
        hist_vals.pop()

    xticks = ['%02.1f' % depth for depth in  np.arange(hist[0],hist[1],(hist[1]-hist[0])/5)]
    xticks.append('%.1f' % hist[1])
    if verbose:
        print xticks  # Why is the 0.0 tick not showing?
    plt.xticks([val * len(hist_vals)/5 for val in range(len(xticks))],xticks) # Yuck!
    plt.fill(range(len(hist_vals)),hist_vals)
    plt.grid(True)
    plt.savefig(basename+'-hist.png') #,dpi=50)


def get_parser():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-b','--bag',
                      help= 'Bag file in the survey')

    parser.add_option('-k','--kml-template',
                      help= 'Template file to fill in [default: %default]')

    parser.add_option('-o','--output-kml',
                      help= 'Where to write the file  [default: stdout]')

    parser.add_option('-s','--survey',
                      help= 'NOAA survey ID.  e.g. H11657')

    parser.add_option('-u','--base-url',
                      help= 'Where will things end up on the server [default: local]')


    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    return parser

if __name__ == '__main__':
    
    (options, args) = get_parser().parse_args()

    print 'bag:',options.bag
    basename = options.bag[:-4]
    template_data = get_template_data(options.survey, basename, options.base_url, options.verbose)
    if options.verbose:
        print 'template_data:',template_data

    kml_content = file("template.kml").read().format(**template_data)

    if options.output_kml is None:
        print kml_content
    else:
        with file(options.output_kml,'w') as kml:
            kml.write( kml_content )

    histogram(basename,options.verbose)
