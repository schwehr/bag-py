#!/usr/bin/env python
from __future__ import print_function

# since 2010-May-28

# Use the sqlite3 db rather than the bads to go much faster and allow for easier development

import sys,os
import sqlite3

def sqlite2kml(cx,outfile):
    cx.row_factory = sqlite3.Row

    o = outfile
    o.write('''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
	<name>NOAA BAGs</name>
        <!-- BAG visualization by Kurt Schwehr -->
        <Style id="bag_style">
          <BalloonStyle>
            <color>ff669999</color>
            <text>$[description]</text>
          </BalloonStyle>
          <IconStyle>
            <Icon><href>http://nrwais1.schwehr.org/~schwehr/bags/bag-icon-66x66.png</href></Icon>
            <hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
          </IconStyle>
        </Style> 

        <Style id="survey_style">
          <BalloonStyle>
            <color>ff669999</color>
            <text>$[description]</text>
          </BalloonStyle>
          <IconStyle>
            <Icon><href>http://nrwais1.schwehr.org/~schwehr/bags/survey-icon-66x66.png</href></Icon>
            <hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
          </IconStyle>
        </Style> 

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
        print(ll,ur)
        dr_url = [row['dr_url'] for row in cx.execute('SELECT dr_url FROM bag WHERE survey=:survey LIMIT 1;',{'survey':survey})][0]
        print (dr_url)
        x_min, y_min = ll
        x_max, y_max = ur
        x_center = (ll[0] + ur[0]) / 2.
        y_center = (ll[1] + ur[1]) / 2.
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
		<name>{survey} descr</name>
                <styleUrl>#survey_style</styleUrl> 
		<description>
<![CDATA[
<p><b>Summary for Survey: {survey}</b></p>
<table border="1">
  <tr><td>Lower left</td><td>{ll[0]} {ll[1]}</td></tr>
  <tr><td>Upper right</td><td>{ur[0]} {ur[1]}</td></tr>
  <tr><td>Descriptive report</td><td><a href="{dr_url}">{survey}.pdf</a> [NGDC]</td></tr>
</table>
]]>
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
            print ('\t',x_min,y_min,x_max,y_max,'->',x_center,y_center,'\t',file)
            o.write('''
	<Placemark>
        <name>{file}</name>
                <styleUrl>#bag_style</styleUrl> 
		<description>
<![CDATA[
<p><b>Summary for BAG: {file}</b></p>
<table border="1">
  <tr><td>Lower left</td><td>{ll[0]} {ll[1]}</td></tr>
  <tr><td>Upper right</td><td>{ur[0]} {ur[1]}</td></tr>
  <tr><td>Descriptive report</td><td><a href="{dr_url}">{survey}.pdf</a> [NGDC]</td></tr>
</table>
]]>
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

'''.format(**locals()) ) # survey=survey, ll=ll, ur=ur, dr_url=dr_url))

        o.write('\t</Folder>\n')

    o.write('''
  </Folder>
</Document>
</kml>
''')
    return

if __name__ == '__main__':
    cx = sqlite3.connect('bags.sqlite')
    sqlite2kml(cx, open('out.kml','w'))

'''
	<Placemark>
		<name>{basename}</name>
                <styleUrl>#bag_style</styleUrl> 
		<description>
<![CDATA[
<table><tr>
    <td><a href="{image}"><img src="{thumb}"/></a></td>
    <td><a href="{histogram}"><img src="{histogram_thumb}"/></a></td>
</tr></table>
<p><b>Summary for BAG: {bag}</b></p>
<table border="1"><!-- <tr><td>Resolution</td><td>{dx_m} x {dy_m} (m)</td></tr> -->
  <!-- <tr><td>Cell </td><td>x x y (m)</td></tr> -->
  <tr><td>Lower left</td><td>{x0} {y0}</td></tr>
  <tr><td>Upper right</td><td>{x1} {y1}</td></tr>
  <tr><td>gdalinfo</td><td><a href="{url}{bag}.info.txt">{bag}.info.txt</a></td></tr>
  <tr><td>xml metadata</td><td><a href="{url}{metadata_xml}">{metadata_xml}</a></td></tr>
  <tr><td>Download bag</td><td><a href="{bag_url}">{survey}.bag.gz</a> [NGDC]</td></tr>
  <tr><td>Descriptive report</td><td><a href="{dr_url}">{survey}.pdf</a> [NGDC]</td></tr>
</table>
]]>
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
</description>
<Point>
<coordinates>{x_center},{y_center}</coordinates>
</Point>
</Placemark>
'''
