#!/usr/bin/env python

import h5py

f = h5py.File('sample.bag')

print f.listobjects()
print f.listitems()

bag_root = f['/BAG_root']
metadata = ''.join(bag_root['metadata'])

print metadata[0:200]

elevation = bag_root['elevation']

print elevation.shape

data = elevation.value
print type(data)
print data
