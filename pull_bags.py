#!/usr/bin/env python

import os

#for i in range(11301,12000):
for i in range(11636,12000):
    cmd = 'wget -c --no-parent -nH --cut-dirs=3 --accept bag.gz,BAG -c -r http://surveys.ngdc.noaa.gov/mgg/NOS/coast/H10001-H12000/H{surveynum}/'.format(surveynum=i)
    os.system(cmd)
