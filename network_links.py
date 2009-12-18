#!/usr/bin/env python
import sys

print '''<?xml version="1.0" encoding="utf-8"?>
<kml xmlns="http://earth.google.com/kml/2.1">
<Document>
<Folder>
'''

for filename in sys.argv[1:]:
    
          
    print '''	    <NetworkLink>
	      <Link>
	        <href>{filename}</href>
	      </Link>
	    </NetworkLink>
'''.format(filename=filename)


print '''</Folder>
</Document>
</kml>
'''
