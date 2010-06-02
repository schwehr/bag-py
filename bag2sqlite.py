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
Create a bounding box and thumb tack for a Bathymetric Attributed Grid (BAG)

@var __date__: Date of last svn commit
@undocumented: __doc__ myparser
@status: under development
@since: 26-May-2010

@requires: U{Python<http://python.org/>} >= 2.6
@requires: U{lxml<http://codespeak.net/lxml/>}
@requires: U{h5py<http://code.google.com/p/h5py/>}
'''


import sys,os
from StringIO import StringIO
from lxml import etree 
import h5py

import sqlite3
from pyproj import Proj

def lon_to_utm_zone(lon):
    return int(( lon + 180 ) / 6) + 1

iso8601_timeformat = '%Y-%m-%dT%H:%M:%SZ'
'for TimeStamp'


def add_bag_to_db(cx, infile_name, survey, filename_base, verbose=False, write_xml=False):
    # filename_base - without .bag or path
    #print ('file:',infile_name, file=sys.stderr)

    v = verbose
    #if v:
    #    print ('opening:',infile_name,os.path.getsize(infile_name))
    f = h5py.File(infile_name) #'H11302_OLS_OSS/H11302_2m_1.bag')
    #o = file('foo.out','w')

    bag_root = f['/BAG_root']
    metadata_xml = ''.join(bag_root['metadata'])
    #o = file('metadata.xml','w')
    #o.write(metadata_xml)
    #del o

    #root = etree.parse(StringIO(metadata_xml)).getroot()
    #root = etree.parse(StringIO(metadata_xml.replace('smXML:',''))).getroot()
    try:
        root = etree.XML(metadata_xml.replace('smXML:',''))
    except:
        print ('bad_metadata:',infile_name) # What can we do?
        return # ouch... better if we could try to fix it somehow
        

    x_min_metadata = float(root.xpath('//*/westBoundLongitude')[0].text)
    x_max_metadata = float(root.xpath('//*/eastBoundLongitude')[0].text)

    y_min_metadata = float(root.xpath('//*/southBoundLatitude')[0].text)
    y_max_metadata = float(root.xpath('//*/northBoundLatitude')[0].text)

    software = root.xpath('//*/BAG_ProcessStep/description')[0].text
    #print ('software:',software)

    utm_zone = int(root.xpath('//*/zone')[0].text)
    # The WGS84 geographic is often foulded up.

    utm_coords = root.xpath('//*/gml:coordinates', namespaces={'gml':"http://www.opengis.net/gml"})[0].text
    #print ('\t',utm_coords)
    utm_coords = utm_coords.split()
    utm_x_min,utm_y_min = [float(coord) for coord in utm_coords[0].split(',')]
    utm_x_max,utm_y_max = [float(coord) for coord in utm_coords[1].split(',')]

    params = {'proj':'utm', 'zone':utm_zone}
    proj = Proj(params)

    x_min,y_min = proj(utm_x_min,utm_y_min, inverse=True)
    x_max,y_max = proj(utm_x_max,utm_y_max, inverse=True)
    #print ('\t',utm_x_min,utm_y_min, utm_x_max,utm_y_max)
    #print ('\t\t',x_min,y_min,x_max,y_max)
    #print ('\t\t',x_min_metadata,y_min_metadata,x_max_metadata,y_max_metadata)
    if abs(x_max - x_max_metadata) > 0.05 or abs(y_max - y_max_metadata) > 0.05:
        print ('%s: %.4f %.4f %.4f %.4f' % (filename_base,
            x_min - x_min_metadata,y_min - y_min_metadata,
            x_max - x_max_metadata,y_max - y_max_metadata)
               )

    vdatum = None
    datums = [entry.text.strip() for entry in root.xpath('//*/datum/RS_Identifier/code')]
    if len(datums)==0:
        pass
    elif 'MLLW' in datums: vdatum = 'MLLW'
    else:
        vdatum = datums[-1] # just guess that it is the last one
        print('datums:',datums,'->',vdatum,filename_base)
        
    axes = (root.xpath('//*/axisDimensionProperties'))
    dx = dy = None
    width = height = None
    for axis in axes:
        #print(etree.tostring(axis, pretty_print=True))
        dim_name = axis.xpath('*/dimensionName')[0].text
        dim_size = int(axis.xpath('*/dimensionSize')[0].text)
        delta = float(axis.xpath('*/*/*/value')[0].text)
        #print ('dim_name: "%s"' % (dim_name,))
        if 'row' == dim_name:
            dy = delta
            height = dim_size
        elif 'column' == dim_name:
            dx = delta
            width = dim_size
        else:
            print ('ERROR: unable to handle dim',dim_name)
            assert False

    # WARNING: This date does not relate to the dates the survey was collected!
    date = root.xpath('//*/CI_Date/date')[0].text 
    abstract = root.xpath('//*/abstract')[0].text
    title = root.xpath('//*/title')[0].text

    timestamp = '' # No timestamp if we can't handle it
    try:
        import datetime, magicdate
        #timestamp = magicdate.magicdate(date)
        creation = magicdate.magicdate(date)
        #timestamp = adate.strftime(iso8601_timeformat) 
    except:
        print ('WARNING: Unable to handle timestamp:',date)
        creation = None

#    if v:
#        print (x_min,x_max,'->',y_min,y_max)
#        print ('date:',date)
#        print ('abstract:',abstract)

    metadata_txt = etree.tostring(root, pretty_print=True ).replace('</',' ').replace('<',' ').replace('>',' ') #.replace('\n','<br/>\n')

    # FIX: base url must change based on the number of the survey
    base_url = 'http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H10001-H12000/'
    dr_url = base_url + survey + '/DR/' + survey + '.pdf'
    bag_url = base_url + survey + '/BAG/' + filename_base + '.bag.gz'

    sql_field_names = ('file', 'survey', 'title','abstract', 'survey', 'creation', 'x_min', 'y_min', 'x_max', 'y_max', 'width', 'height', 'dx', 'dy', 'vdatum', 'utm_zone', 'dr_url', 'bag_url', 'metadata_txt','metadata_xml', 'utm_x_min','utm_y_min' ,  'utm_x_max' ,'utm_y_max', 'software')

    file = filename_base

    # check for errors
    #for field in sql_field_names:
    #    print('%s:' % (field,) ,locals()[field])

    sql_insert = 'INSERT INTO bag (' + ','.join(sql_field_names) + ') VALUES (' + ', '.join([':%s' %(field,) for field in sql_field_names ]) + ');'

    #print (bag_data)
    #print (sql_insert)
    cx.execute(sql_insert,locals()) # Passing locals sees crazy
    cx.commit()

def parse_filename(filename_full):
    # e.g. /Users/schwehr/Desktop/bags/H10001-H12000/H11411/BAG/H11411_2m_12.bag
    # Take survey from the directory, not the filename
    filename_full = os.path.abspath(filename_full) # Make sure we can get the survey
    base, filename = os.path.split(filename_full)
    filename, ext = os.path.splitext(filename)

    survey = base.split(os.path.sep)[-2]
    return survey, filename

def create_table(cx):

    create_sql = '''
CREATE TABLE IF NOT EXISTS bag (
       id INTEGER PRIMARY KEY, -- AUTOINCREMENT NOT NULL UNIQUE,
       file VARCHAR, -- NOT NULL UNIQUE,
       survey VARCHAR, -- NOT NULL,
       title TEXT,
       abstract TEXT,
       creation DATETIME, -- Unfortunetly nothing to do with the survey
       x_min FLOAT, -- NOT NULL,
       y_min FLOAT, -- NOT NULL,
       x_max FLOAT, -- NOT NULL,
       y_max FLOAT, -- NOT NULL,
       width INTEGER, -- NOT NULL,
       height INTEGER, -- NOT NULL,
       dx FLOAT, -- NOT NULL, -- m
       dy FLOAT, -- NOT NULL, -- m
       utm_zone INTEGER, -- NOT NULL,
       utm_x_min FLOAT, -- NOT NULL,
       utm_y_min FLOAT, -- NOT NULL,
       utm_x_max FLOAT, -- NOT NULL,
       utm_y_max FLOAT, -- NOT NULL,
       vdatum VARCHAR, -- NOT NULL
       dr_url TEXT, -- NOT NULL -- Descriptive report at NGDC
       bag_url TEXT, -- NOT NULL -- The original BAG file at NGDC
       software TEXT, -- Software used to create the bag so we can track troubles
       metadata_txt TEXT,
       metadata_xml TEXT
       -- metadata_html TEXT,
       -- gdal_info TEXT,
);
'''
    cx.execute(create_sql)
    cx.commit()
    
def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.bag [file2.bag] ...",
                          version="%prog "+__version__+' ('+__date__+')')
    
    #parser.add_option('--create', default=False, action='store_true', help='Create the db table')
    parser.add_option('-d', '--database', default='bags.sqlite', help='Sqlite3 database to use')
    parser.add_option('-v', '--verbose', default=False, action='store_true', help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose
    
    cx = sqlite3.connect('bags.sqlite')
    #cx.row_factory = sqlite3.Row

    create_table(cx)

    #infile_name = 'H11401_2m_1.bag'
    #survey='H11401'
    #verbose = True
    for cnt, filename_full in enumerate(args):
        survey,filename = parse_filename(filename_full)
        if v and cnt % 100 == 0:
            print (cnt,filename)

        #if v: print ('processing_bag:',survey,filename,filename_full, file=sys.stderr)
        add_bag_to_db(cx, filename_full, survey, filename, v)

if __name__ == '__main__':
    main()
