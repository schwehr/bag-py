#!/usr/bin/env python
from __future__ import print_function

import sys, os
import osgeo.gdal
import osgeo.gdalconst
osgeo.gdal.AllRegister()

import numpy as np
import matplotlib.pyplot as plt

__version__='0.1'
__date__='?'

def get_template_data(bag_file, survey, basename, urlbase, verbose):

    if urlbase is None:
        urlbase = ''
    elif urlbase[-1] != '/':
        urlbase += '/'
    url = urlbase

    patch_name = basename.split('/')[-1]
    print ('base_name',basename)
    print ('patch_name',patch_name)
    #sys.exit('EARLY')

    td = {} # template_dict/data
    #td['urlbase'] = 'http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/{survey}/{patch}'.format(survey=survey, patch=patch_name)
    td['survey'] = survey
    td['basename'] = patch_name
    td['patch'] = patch_name
    td['bag'] = patch_name + '.bag'
    td['thumb'] = url + patch_name + '-thumb.jpg'
    td['image'] = url + patch_name + '.jpg'
    td['url'] = url #urlbase

    # NGDC download bag link
    td['bag_url'] = 'http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H10001-H12000/{survey}/BAG/{basename}.bag.gz'.format(**td)
    #print ('bag_rl:'.td['bag_url'])

    td['dr_url'] = 'http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H10001-H12000/{survey}/DR/{survey}.pdf'.format(**td)
    #print ('dr_url:',td['dr_url'])

    #td['info'] = url +  patch_name + '.info.txt'

    osgeo.gdal.AllRegister()

    bag = osgeo.gdal.Open(bag_file)
    assert bag
    gt_bag =  bag.GetGeoTransform()
    td['dx_m'] = '%02.1f' % gt_bag[1]
    td['dy_m'] = '%02.1f' % gt_bag[5]

    w,h = bag.RasterXSize,bag.RasterYSize
    td['w'] = w
    td['h'] = h


    print ('Opening:',patch_name + '.tif')
    patch = osgeo.gdal.Open(patch_name + '.tif')
    if patch is None:
        raise ValueError('Unable to open patch')

    w,h = patch.RasterXSize,patch.RasterYSize
    #td['w'] = w
    #td['h'] = h
    gt =  patch.GetGeoTransform()
    gt_dict = {'ul_x':gt[0], 'x_res':gt[1], 'ul_y':gt[3], 'y_res':gt[5]}
    if verbose:
        print (gt_dict)

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

    td['histogram'] = url + patch_name + '-hist.jpg'
    td['histogram_thumb'] = url + patch_name + '-hist-thumb.jpg'
    td['cwd'] = os.getcwd()
    td['metadata_xml'] = patch_name + '.metadata.xml'

    return td

def histogram_gdal_direct(bag_file, patch_name,verbose):
    # This is the one 
    'Plot the depth histogram.  Use the tif until gdal 1.7.0 comes out'

    patch = osgeo.gdal.Open(bag_file)
    band = patch.GetRasterBand(1)
    bandmin,bandmax = band.ComputeRasterMinMax()
    hist = band.GetDefaultHistogram()

    #print hist
    #print '----------------------------------------------------------------------'
    #print hist[3]
    hist_vals = hist[3][:-1]
    while hist_vals[-1] == 0:
        hist_vals.pop()

    xticks = ['%02.1f' % depth for depth in  np.arange(hist[0],hist[1],(hist[1]-hist[0])/5)]
    xticks.append('%.1f' % hist[1])
    if verbose:
        print (xticks)  # Why is the 0.0 tick not showing?
    plt.xticks([val * len(hist_vals)/5 for val in range(len(xticks))],xticks) # Yuck!
    plt.fill(range(len(hist_vals)),hist_vals)
    plt.grid(True)
    plt.savefig(patch_name+'-hist.png') #,dpi=50)
    with file(patch_name+'.hist','w') as o:
        o.write('\n'.join([str(v) for v in hist_vals]))


def histogram_gdal_info_file(patch, verbose):
    'Plot the depth histogram.  Use the tif until gdal 1.7.0 comes out'
    # This one to use the svn gdal with bag support.  

    with file(patch+'.bag.info.txt') as info:
        line = info.readline()
        while 'buckets' not in line:
            line = info.readline()
            continue
        fields = line.split()
        minval,maxval = float(fields[3]),float(fields[5].rstrip(':'))
        
        #print minval,maxval
        #print 'line:',line
        line = info.readline()
        #print 'line:',line
        hist = [int(val) for val in line.split()]

        #print

    #print (hist)
    hist_vals = hist[:-1]
    while hist_vals[-1] == 0:
        hist_vals.pop()

    xticks = ['%02.1f' % depth for depth in  np.arange(minval,maxval,(maxval-minval)/5)]
    xticks.append('%.1f' % maxval)
    if verbose:
        print (xticks)  # Why is the 0.0 tick not showing?
    plt.xticks([val * len(hist_vals)/5 for val in range(len(xticks))],xticks) # Yuck!
    #print 'plotting:',range(len(hist_vals)),hist_vals
    x = [0,] + range(len(hist_vals)) + [len(hist_vals),]
    y = [0,] + hist_vals + [0,]
    plt.fill(x,y)
    plt.grid(True)
    plt.xlabel('Depth (m)')
    plt.ylabel('Cell counts')
    plt.title ('Histogram of cell depths for '+patch)

    plt.savefig(patch+'-hist.png') #,dpi=50)
    with file(patch+'.hist','w') as o:
        o.write('\n'.join([str(v) for v in hist_vals]))

#     with file(basename+'.hist2','w') as o:
#         x = (range(len(hist_vals)))
#         #print len(x), len(hist_vals)
#         for i in range(len(hist_vals)):
#             o.write('%f %f\n' % (x[i],hist_vals[i]))


def get_parser():
    '''
    FIX: document main
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-b','--bag',
                      help= 'Bag file in the survey with path')

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

    patch = os.path.basename(options.bag).split('.')[0] # just something like H11124_5m
    print ('patch:',patch)
    print ('bag:',options.bag)
    basename = options.bag[:-4]
    template_data = get_template_data(options.bag, options.survey, basename, options.base_url, options.verbose)
    if options.verbose:
        print ('template_data:',template_data)

    kml_content = file(options.kml_template).read().format(**template_data)

    if options.output_kml is None:
        print (kml_content)
    else:
        with file(options.output_kml,'w') as kml:
            kml.write( kml_content )

    #histogram(basename,options.verbose)
    histogram_gdal_info_file(patch, options.verbose)
    #histogram_gdal_direct(options.bag, patch)
