#!/usr/bin/env python

import h5py

f = h5py.File('H11302_OLS_OSS/H11302_2m_1.bag')

#print f.listobjects()
#print f.listitems()

bag_root = f['/BAG_root']
metadata_xml = ''.join(bag_root['metadata'])
o = file('metadata.xml','w')
o.write(metadata_xml)
del o

from lxml import etree 
from StringIO import StringIO
#root = etree.parse(StringIO(metadata_xml)).getroot()
#root = etree.parse(StringIO(metadata_xml.replace('smXML:',''))).getroot()
root = etree.XML(metadata_xml.replace('smXML:',''))
#print(etree.tostring(root, pretty_print=True))



xmin = float(root.xpath('//*/westBoundLongitude')[0].text)
xmax = float(root.xpath('//*/eastBoundLongitude')[0].text)

ymin = float(root.xpath('//*/southBoundLatitude')[0].text)
ymax = float(root.xpath('//*/northBoundLatitude')[0].text)

print xmin,xmax,'->',ymin,ymax

date = root.xpath('//*/CI_Date/date')[0].text

print 'date:',date

abstract = root.xpath('//*/abstract')[0].text
print 'abstract:',abstract

import subprocess
p = subprocess.Popen(
    ['source-highlight','-s', 'xml', '--out-format=html'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE
    )

metadata_html = p.communicate(input=etree.tostring(root, pretty_print=True ) ) [0]

print metadata_html
kml_data = {
    'title':'%s : %s'%(abstract,date),
    'x': (xmin+xmax)/2.,
    'y': (ymin+ymax)/2.,
    'xmin':xmin, 
    'xmax':xmax,
    'ymin':ymin,
    'ymax':ymax,
    'metadata': metadata_html
}

o = file('out.kml','w')
o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>

	<Placemark>
		<name>{title}</name>
		<description><!-- <pre> <![CDATA[ -->
{metadata}
<!-- ]]> </pre> -->
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
</Document>
</kml>
'''.format(**kml_data)
)
