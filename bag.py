#!/usr/bin/env python

import h5py

f = h5py.File('H11302_OLS_OSS/H11302_2m_1.bag')

print f.listobjects()
print f.listitems()

bag_root = f['/BAG_root']
metadata = ''.join(bag_root['metadata'])
o = file('metadata.xml','w')
o.write(metadata)
del o


#print metadata #[0:200]

elevation = bag_root['elevation']

print 'shape:',elevation.shape

data = elevation.value
#print type(data)
#print data

print 'range:',data.min(), data.max()

#import matplotlib.mlab as mlab
#import matplotlib.pyplot as plt

o = file('out.xyz','w')
for y in range(elevation.shape[1]):
    #for x,z in enumerate(elevation[y]):
    for x in range(elevation.shape[0]):
        z = elevation[x,y]
        if z>=1000000-1:
            continue
        #o.write('{x} {y} {z}\n'.format(x=x,y=y,z=z))
        o.write('%d %d %0.2f\n'% (x,y,z))
