#!/usr/bin/env bash

#text_type= ""

in=survey-icon-66x66.png

count=1
while [[ $count -le 9 ]]; do
   #echo $count
    #rm survey-icon-66x66-$count.png
    # -fill red
    convert -fill brown -draw "circle 51,51 61,61" -fill white -pointsize 20 -annotate +46+59 $count $in survey-icon-66x66-$count.png
   let count=$count+1
done

count=10
while [[ $count -le 30 ]]; do
    convert -fill brown -draw "circle 51,51 61,61" -fill white -pointsize 20 -annotate +40+59 $count $in survey-icon-66x66-$count.png
    let count=$count+1
done 
