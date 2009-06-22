#!/usr/bin/env python

#!/usr/bin/env python
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


def bag2kmlbbox(in_name,out_file, title=None, kml_complete=False, verbose=False):
    v = verbose
    f = h5py.File(in_name) #'H11302_OLS_OSS/H11302_2m_1.bag')
    #o = file(out_name,'w')
    # FIX: if out_file is a string, then open
    o = out_file
    #print f.listobjects()
    #print f.listitems()

    bag_root = f['/BAG_root']
    metadata_xml = ''.join(bag_root['metadata'])
    #o = file('metadata.xml','w')
    #o.write(metadata_xml)
    #del o

    #root = etree.parse(StringIO(metadata_xml)).getroot()
    #root = etree.parse(StringIO(metadata_xml.replace('smXML:',''))).getroot()
    root = etree.XML(metadata_xml.replace('smXML:',''))

    xmin = float(root.xpath('//*/westBoundLongitude')[0].text)
    xmax = float(root.xpath('//*/eastBoundLongitude')[0].text)

    ymin = float(root.xpath('//*/southBoundLatitude')[0].text)
    ymax = float(root.xpath('//*/northBoundLatitude')[0].text)

    date = root.xpath('//*/CI_Date/date')[0].text
    abstract = root.xpath('//*/abstract')[0].text

    if v:
        print xmin,xmax,'->',ymin,ymax
        print 'date:',date
        print 'abstract:',abstract

    #import subprocess
    #p = subprocess.Popen(
    #    ['source-highlight','-s', 'xml', '--out-format=html'],
    #    stdin=subprocess.PIPE,
    #    stdout=subprocess.PIPE
    #    )
    #metadata_html = p.communicate(input=etree.tostring(root, pretty_print=True ) ) [0]

    metadata_html = etree.tostring(root, pretty_print=True ).replace('</',' ').replace('<',' ').replace('>',' ') #.replace('\n','<br/>\n')

    if v: print metadata_html

    if not title:
        title = '%s : %s'%(abstract,date)

    kml_data = {
        'title': title,
        'x': (xmin+xmax)/2.,
        'y': (ymin+ymax)/2.,
        'xmin':xmin, 
        'xmax':xmax,
        'ymin':ymin,
        'ymax':ymax,
        'metadata': metadata_html
        }

    #o = file('out.kml','w')
    if kml_complete:
        o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>''')

    o.write('''
	<Placemark>
		<name>{title}</name>
		<description><![CDATA[
<pre>
{metadata}
</pre>
]]>
		</description>
		<Point> <coordinates> {x},{y},0 </coordinates> </Point>
	</Placemark>

	<Placemark>
		<name>{title}</name>
		<LineString>
			<coordinates>
{xmin},{ymin},0
{xmax},{ymin},0
{xmax},{ymax},0
{xmin},{ymax},0
{xmin},{ymin},0
			</coordinates>
		</LineString>
	</Placemark>
'''.format(**kml_data)
)

    if kml_complete:
        o.write('''</Document>
</kml>
''')

    return

def main():
    from optparse import OptionParser

    # FIX: is importing __init__ safe?
    parser = OptionParser(usage="%prog [options]"
                          ,version="%prog "+__version__ + " ("+__date__+")")

#    parser.add_option('-i','--in-file',dest='infile_name',
#                      help='BAG to read')
    parser.add_option('-o','--out-file',dest='outfile_name',default='bag.kml',
                      help='KML to write')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
                      help='Make the test output verbose')
    (options,args) = parser.parse_args()
    v = options.verbose 

    o = file(options.outfile_name,'w')

    o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>''')

    for filename in args:
        print filename
        try:
            bag2kmlbbox(filename, o, title=os.path.basename(filename), verbose=v)
        except:
            continue

    o.write('''</Document>
</kml>
''')


if __name__ == '__main__':
    main()
