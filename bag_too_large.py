#!/usr/bin/env python

import subprocess
import sys

filename = sys.argv[1]
max_dim = int (sys.argv[2])

class gdalinfo:
    def __init__(self, filename):
        # FIX: replace all this with the gdal python interface with gdal 1.7.0
        proc = subprocess.Popen('~/local/bin/gdalinfo %s' % filename, shell=True, stdout=subprocess.PIPE)
        stdout = proc.communicate()[0].split('\n')
        #print stdout

        #print stdout[0]
        self.driver = stdout[0].split(':')[1].strip()
        #print stdout[2]
        self.w = int(stdout[2].split('is')[1].split(',')[0])
        self.h = int(stdout[2].split(',')[1])
    
        #print self.w, self.h



info = gdalinfo(filename)

#print 'max_dim:', max_dim
#print 'dims:',info.w,info.h

if max_dim < info.w:
    #print "width too large"
    sys.exit(1)
if max_dim < info.h:
    #print "height too large"
    sys.exit(1)

sys.exit(0)
