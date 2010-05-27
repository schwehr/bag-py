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

import sqlite3
cx = sqlite3.connect('bags.sqlite')
#cx.row_factory = sqlite3.Row

iso8601_timeformat = '%Y-%m-%dT%H:%M:%SZ'
'for TimeStamp'

infile_name = 'H11401_2m_1.bag'
survey='H11401'
verbose = True

if True:
    v = verbose
    f = h5py.File(infile_name) #'H11302_OLS_OSS/H11302_2m_1.bag')
    o = file('foo.out','w')

    bag_root = f['/BAG_root']
    metadata_xml = ''.join(bag_root['metadata'])
    o = file('metadata.xml','w')
    o.write(metadata_xml)
    del o

    #root = etree.parse(StringIO(metadata_xml)).getroot()
    #root = etree.parse(StringIO(metadata_xml.replace('smXML:',''))).getroot()
    root = etree.XML(metadata_xml.replace('smXML:',''))

    x_min = float(root.xpath('//*/westBoundLongitude')[0].text)
    x_max = float(root.xpath('//*/eastBoundLongitude')[0].text)

    y_min = float(root.xpath('//*/southBoundLatitude')[0].text)
    y_max = float(root.xpath('//*/northBoundLatitude')[0].text)

    utm_zone = int(root.xpath('//*/zone')[0].text)
    vdatum = None
    for entry in root.xpath('//*/datum/RS_Identifier/code'):
        print (entry.text)
        if entry.text != 'NAD83': # NAD83 is not a vertical reference datum folks
            vdatum = entry.text
            break
        
    axes = (root.xpath('//*/axisDimensionProperties'))
    dx = dy = None
    width = height = None
    for axis in axes:
        #print(etree.tostring(axis, pretty_print=True))
        dim_name = axis.xpath('*/dimensionName')[0].text
        dim_size = int(axis.xpath('*/dimensionSize')[0].text)
        delta = float(axis.xpath('*/*/*/value')[0].text)
        print ('dim_name: "%s"' % (dim_name,))
        if 'row' == dim_name:
            dy = delta
            height = dim_size
        elif 'column' == dim_name:
            dx = delta
            width = dim_size
        else:
            assert False

    # WARNING: This date does not relate to the dates the survey was collected!
    date = root.xpath('//*/CI_Date/date')[0].text 
    abstract = root.xpath('//*/abstract')[0].text

    timestamp = '' # No timestamp if we can't handle it
    try:
        import datetime, magicdate
        timestamp = magicdate.magicdate(date)
        #timestamp = adate.strftime(iso8601_timeformat) 
    except:
        print ('WARNING: Unable to handle timestamp:',date)
        timestamp = None

    if v:
        print (x_min,x_max,'->',y_min,y_max)
        print ('date:',date)
        print ('abstract:',abstract)

    metadata_html = etree.tostring(root, pretty_print=True ).replace('</',' ').replace('<',' ').replace('>',' ') #.replace('\n','<br/>\n')
    title = 'too long...'

    # FIX: base url must change based on the number of the survey
    base_url = 'http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H10001-H12000/'
    dr_url = base_url + survey + '/DR/' + survey + '.pdf'
    bag_url = base_url + survey + '/BAG/' + infile_name + '.gz'

    sql_field_names = ('file', 'survey', 'title','abstract', 'survey', 'creation', 'x_min', 'y_min', 'x_max', 'y_max', 'width', 'height', 'dx', 'dy', 'vdatum', 'utm_zone', 'dr_url', 'bag_url')

    file = infile_name
    print ('file:',file)
    creation = timestamp

    # check for errors
    for field in sql_field_names:
        print('%s:' % (field,) ,locals()[field])

    sql_insert = 'INSERT INTO bag (' + ','.join(sql_field_names) + ') VALUES (' + ', '.join([':%s' %(field,) for field in sql_field_names ]) + ');'

    #print (bag_data)
    print (sql_insert)
    cx.execute(sql_insert,locals()) # Passing locals sees crazy
    cx.commit()
