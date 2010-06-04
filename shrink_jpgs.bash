#!/bin/bash

# Compress all files over 100k

for dir in `find processed -maxdepth 1 -type d -name "H*"`; do
    echo dir: $dir
    echo -n "  before: "
    du -hs $dir
    for file in `find $dir -name \*.jpg -size +100k`; do
        #echo "  $file"
        ./bag_too_large.py -f $file -m 1000
        if [ 1 == $? ]; then
            echo "    $file"
            #echo -n "  "
            #identify $file
            convert -resize '1000x1000>' -quality 40 $file tmp.jpg
            mv tmp.jpg $file
        fi
    done
    echo -n "  after: "
    du -hs $dir
done