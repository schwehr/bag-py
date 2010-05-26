#!/usr/bin/env python
import colorsys

def cpt2rgb(h,s,v):
    'input in cpt style... h 0..255 s and v 0.0 to 1.0'
    h = fields[1] / 360.
    s = fields[2]
    v = fields[3]
    rgb = colorsys.hsv_to_rgb(h,s,v)
    return [int(color*255) for color in rgb]

colors = []
for line in file('cpt'):
    if line[0] in ('#','B','N','F'):
        continue
    fields = [float(field) for field in line.split()]
    colors.append( cpt2rgb (*fields[1:4]) )

for i,color in enumerate(colors):
    color = (int(float(i)/len(colors)*100), ) + tuple(color)
    print '%d%% %3d %3d %3d' % color

print 'nv    0   0   0'
    
