#!/usr/bin/env python
from __future__ import print_function

__author__ = 'Kurt Schwehr'
__version__ = '$Revision: 2275 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-07-10 16:22:35 -0400 (Mon, 10 Jul 2006) $'.split()[1]
__copyright__ = '2010'
__license__   = 'Apache 2.0'
__contact__   = 'schwehr@gmail.com'


# since 2010-May-28

# Use the sqlite3 db rather than the bads to go much faster and allow for easier development

import sys,os
import sqlite3

def sqlite2kml_bbox_and_placemark(cx,outfile,
               icon_base_url = 'file:///Users/schwehr/projects/src/bag-py',
               custom_products_base_url = 'file:///Users/schwehr/projects/src/bag-py/processed'):
    cx.row_factory = sqlite3.Row

    o = outfile
    o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
	<name>NOAA BAGs - Summaries</name>
        <!-- BAG visualization by Kurt Schwehr -->
        <Style id="bag_style">
          <BalloonStyle>
            <color>ff669999</color>
            <text>$[description]</text>
          </BalloonStyle>
          <IconStyle>
            <Icon><href>{icon_base_url}/bag-icon-66x66.png</href></Icon>
            <hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
          </IconStyle>
        </Style> 

        <Style id="survey_style">
          <BalloonStyle>
            <color>ff669999</color>
            <text>$[description]</text>
          </BalloonStyle>
          <IconStyle>
            <Icon><href>{icon_base_url}/survey-icon-66x66.png</href></Icon>
            <hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
          </IconStyle>
        </Style> 
'''.format(**locals()) )
            
    for i in range(70):
        o.write('''\t<Style id="survey_{count}_style">
          <BalloonStyle>
            <color>ff669999</color>
            <text>$[description]</text>
          </BalloonStyle>
          <IconStyle>
            <Icon><href>{icon_base_url}/survey-icon-66x66-{count}.png</href></Icon>
            <hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
          </IconStyle>
        </Style>
'''.format(count=i, **locals()))
            
    o.write('''
	<Style id="survey_bbox">
		<LineStyle>
			<color>ff0074d2</color>
			<width>2</width>
		</LineStyle>
	</Style>
  <Folder>
''')

    surveys = [row['survey'] for row in cx.execute('SELECT DISTINCT(survey) FROM bag;')]
    #print (surveys[:10])
    for survey in surveys: #[:2]: 
        print ('Processing:',survey)
        ll = [row for row in cx.execute('SELECT MIN(x_min) as x, MIN(y_min) as y FROM bag WHERE survey=:survey;',{'survey':survey})][0]
        ur = [row for row in cx.execute('SELECT MAX(x_max) as x, MAX(y_max) as y FROM bag WHERE survey=:survey;',{'survey':survey})][0]
        #print(ll,ur)
        dr_url = [row['dr_url'] for row in cx.execute('SELECT dr_url FROM bag WHERE survey=:survey LIMIT 1;',{'survey':survey})][0]
        #print (dr_url)
        x_min, y_min = ll
        x_max, y_max = ur
        x_center = (ll[0] + ur[0]) / 2.
        y_center = (ll[1] + ur[1]) / 2.

        bag_count = [row for row in cx.execute('SELECT COUNT(*) as bag_count FROM bag WHERE survey=:survey;',{'survey':survey})][0]['bag_count']
        #print ('bag_count:',bag_count)
        
        survey_url = dr_url[:dr_url.rfind('/')].rstrip('DR')
        #print ('\t',survey_url)
        o.write('''
        <Folder><name>{survey}</name>
        <Placemark>
		<name>{survey} bbox</name>
		<styleUrl>#survey_bbox</styleUrl> 
		<LineString>
			<altitudeMode>relativeToGround</altitudeMode>
			<coordinates>
{x_min},{y_min},100
{x_max},{y_min},100
{x_max},{y_max},100
{x_min},{y_max},100
{x_min},{y_min},100
			</coordinates>
		</LineString>
	</Placemark>
        <Folder><name>{survey} descr</name>
	<Region>
		<LatLonAltBox>
			<north>{y_max}</north>
			<south>{y_min}</south>
			<east>{x_max}</east>
			<west>{x_min}</west>
			<minAltitude>0</minAltitude>
			<maxAltitude>0</maxAltitude>
		</LatLonAltBox>
		<Lod>
			<minLodPixels>-1</minLodPixels>
			<maxLodPixels>200</maxLodPixels>
			<minFadeExtent>0</minFadeExtent>
			<maxFadeExtent>0</maxFadeExtent>
		</Lod>
	</Region>
	<Placemark>
		<name>{survey}</name>
                <styleUrl>#survey_{bag_count}_style</styleUrl> 
		<description>
<![CDATA[
<p><b>Summary for Survey: {survey}</b></p>
<table border="1">
  <tr><td>Lower left</td><td>{ll[0]} {ll[1]}</td></tr>
  <tr><td>Upper right</td><td>{ur[0]} {ur[1]}</td></tr>
  <tr><td>Descriptive report</td><td><a href="{dr_url}">{survey}.pdf</a> [NGDC]</td></tr>
  <tr><td>Survey directory</td><td><a href="{survey_url}">{survey}</a> [NGDC]</td></tr>
</table>
]]>
<hr/>
<center>
<table>
  <tr>
    <td><a href="http://ccom.unh.edu/"><img src="{icon_base_url}/ccom-logo-border.png"/></a></td>
    <td><a href="http://noaa.gov/"><img src="{icon_base_url}/noaa-logo-border.png"/></a></td>
  </tr>
</table>
Visualization by: <a href="http://schwehr.org/">Kurt Schwehr et al.</a>
</center>
</description>
<Point>
<coordinates>{x_center},{y_center}</coordinates>
</Point>
        </Placemark>
        </Folder> <!-- keep the region just to the overview placemark -->
        </Folder>

        <Folder> <name>{survey} bags</name>
	<Region>
		<LatLonAltBox>
			<north>{y_max}</north>
			<south>{y_min}</south>
			<east>{x_max}</east>
			<west>{x_min}</west>
			<minAltitude>0</minAltitude>
			<maxAltitude>0</maxAltitude>
		</LatLonAltBox>
		<Lod>
			<minLodPixels>200</minLodPixels>
			<maxLodPixels>-1</maxLodPixels>
			<minFadeExtent>0</minFadeExtent>
			<maxFadeExtent>0</maxFadeExtent>
		</Lod>
	</Region>
'''.format(**locals()))
        
        ######################################################################
        # Individual BAGs
        for bag in cx.execute('SELECT * FROM bag WHERE survey=:survey;',{'survey':survey}):
            #print ('\t',bag['x_min'],bag['y_min'],bag['x_max'],bag['y_max'],bag['file'])
            x_min = bag['x_min']; x_max = bag['x_max']; x_center = (x_min + x_max) / 2
            y_min = bag['y_min']; y_max = bag['y_max']; y_center = (y_min + y_max) / 2
            file = bag['file']
            #print ('\t',x_min,y_min,x_max,y_max,'->',x_center,y_center,'\t',file)

            base_tmp = custom_products_base_url + '/' + survey + '/' + bag['file']
            image = base_tmp + '.jpg'
            thumb = base_tmp + '-thumb.jpg'          
            hist = base_tmp + '-hist.jpg'          
            hist_thumb = base_tmp + '-hist-thumb.jpg'          

            #gdal_info_url = custom_products_base_url + '/' + survey + '
            bag = dict(bag)
            bag.update(locals()) # Pull in survey url and such
            o.write('''
	<Placemark>
        <name>{file}</name>
                <styleUrl>#bag_style</styleUrl> 
		<description>
<![CDATA[
<table><tr>
    <td><a href="{image}"><img src="{thumb}"/></a></td>
    <td><a href="{hist}"><img src="{hist_thumb}"/></a></td>
</tr></table>

<p><b>Summary for BAG: {file}</b></p>
<table border="1">
  <tr><td>Resolution</td><td>{dx} x {dy} (m/cell)</td></tr> 
  <tr><td>Cells </td><td>{width} x {height} (m)</td></tr>
  <tr><td>Lower left</td><td>{ll[0]} {ll[1]}</td></tr>
  <tr><td>Upper right</td><td>{ur[0]} {ur[1]}</td></tr>
  <tr><td>Descriptive report</td><td><a href="{dr_url}">{survey}.pdf</a> [NGDC]</td></tr>
  <tr><td>gdalinfo</td><td><a href="{base_tmp}.bag.info.txt">{file}.bag.info.txt</a></td></tr>
  <tr><td>xml metadata</td><td><a href="{base_tmp}.metadata.xml">{file}.metadata.xml</a></td></tr>
  <tr><td>Download bag</td><td><a href="{bag_url}">{file}.bag.gz</a> [NGDC]</td></tr>
</table>
<hr/>
<center>
<table>
  <tr>
    <td><a href="http://ccom.unh.edu/"><img src="http://nrwais1.schwehr.org/~schwehr/bags/ccom-logo-border.png"/></a></td>
    <td><a href="http://noaa.gov/"><img src="http://nrwais1.schwehr.org/~schwehr/bags/noaa-logo-border.png"/></a></td>
  </tr>
</table>
Visualization by: <a href="http://schwehr.org/">Kurt Schwehr et al.</a>
</center>
]]>
</description>
<Point>
<coordinates>{x_center},{y_center}</coordinates>
</Point>
</Placemark>

	<Placemark>
		<name>{survey}</name>
		
		<LineString>
			<coordinates>
{x_min},{y_min},0
{x_max},{y_min},0
{x_max},{y_max},0
{x_min},{y_max},0
{x_min},{y_min},0
			</coordinates>
		</LineString>
	</Placemark>

'''.format(**bag) ) # survey=survey, ll=ll, ur=ur, dr_url=dr_url))
#'''.format(**locals()) ) # survey=survey, ll=ll, ur=ur, dr_url=dr_url))

        o.write('\t</Folder>\n')

    o.write('''
  </Folder>
</Document>
</kml>
''')
    return


################################################################################
# Tiled
####
def sqlite2kml_tiled(cx, outfile,
                     custom_products_base_url = 'file:///Users/schwehr/projects/src/bag-py/processed'):

    cx.row_factory = sqlite3.Row

    o = outfile
    o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
	<name>NOAA BAGs - Tiled</name>
        <!-- BAG visualization by Kurt Schwehr -->
''')

    for cnt,bag in enumerate(cx.execute('SELECT * FROM bag;')):
        if cnt % 200 == 0: print (cnt)
        #print ('\t',bag['x_min'],bag['y_min'],bag['x_max'],bag['y_max'],bag['file'])
        x_min = bag['x_min']; x_max = bag['x_max']; x_center = (x_min + x_max) / 2
        y_min = bag['y_min']; y_max = bag['y_max']; y_center = (y_min + y_max) / 2
        file = bag['file']
        bag = dict(bag)
        tile_url = custom_products_base_url + '/' +bag['survey'] + '/' + file + '/' + file + '-bathy.kml'
        bag.update(locals())
        # FIX: possibly add a region to the network link to prevent loading from the server
        o.write('''
<NetworkLink>
  <Link><href>{tile_url}</href></Link>
</NetworkLink>
        '''.format(**bag))

    #   </Folder>
    o.write('''
</Document>
</kml>
''')
    return


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options] file1.bag [file2.bag] ...",
                          version="%prog "+__version__+' ('+__date__+')')
    # FIX: need to somehow allow for surveys that are in multiple subfolders
    parser.add_option('--custom-products-url', default='http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/', help=' [default: %default]')
    parser.add_option('--icon-url', default='http://nrwais1.schwehr.org/~schwehr/bags/', help=' [default: %default]')
    parser.add_option('-d', '--database', default='bags.sqlite', help='Sqlite3 database to use')
    parser.add_option('-v', '--verbose', default=False, action='store_true', help='run the tests run in verbose mode')

    parser.add_option('--bbox-and-placemark-kml', default='bag_summary.kml', help=' [default: %default]')
    parser.add_option('--tiled-kml', default='bag_surveys.kml', help=' [default: %default]')
    #parser.add_option('--', default=, help=' [default: %default]')


    (options, args) = parser.parse_args()
    v = options.verbose

    cx = sqlite3.connect(options.database)

    sqlite2kml_bbox_and_placemark(cx, open(options.bbox_and_placemark_kml,'w'),
                                  options.icon_url, options.custom_products_url)

    sqlite2kml_tiled(cx, open(options.tiled_kml,'w'),
                     options.custom_products_url)


if __name__ == '__main__':
    main()
