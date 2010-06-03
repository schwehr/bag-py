#!/usr/bin/env bash 
# -e

#set -x # Turn on Debugging

# 2010-05: Turning off compress and metadata generation.  Metadata comes from the sqlite process.

# Convert all BAGs from NGDC into KML visualizations

# /Volumes/KURT2009-1/BAGs/ngdc

#mkdir -p processed

#rm -f processed/*/*.{tif,grd}
#rm -f processed/*/*color*.{tif,grd}

#rm -rf processed

PATH=`pwd`:$PATH


#for compressed_file in `find ./H10001-H12000/ -name \*.bag.gz`; do 

#for compressed_file in `find . -name \*.bag.gz | head -1`; do 
#for compressed_file in H10001-H12000/H11334/BAG/H11334_5m.bag.gz; do
#for compressed_file in `cat bags.find`; do 
for bag_file in `cat find.bag`; do 
    echo
    echo "BAG: $bag_file"
    basename=`basename $bag_file`
    echo "basename: $basename"
    src=`basename ${bag_file}`
    echo "src: $src"
    survey=`echo $bag_file | cut -f3 -d/ `
    echo "survey: $survey"

    patch=${src%%.bag}
    echo "patch: $patch"

    mkdir -p processed/$survey
    #gzcat $compressed_file > processed/$survey/$src
#if [ 1 == $? ]; then
    pushd processed/$survey
        bag_file=../../$bag_file 
        #rm -f *.png *.tif *.jpg 
        echo Processing patch: $patch

        # Get the basic info references
        # FIX: renable this one
        gdalinfo -hist $bag_file > $patch.bag.info.txt

        echo ../../bag_xml_dump.py -b $bag_file -o $patch.metadata.xml
        ../../bag_xml_dump.py -b $bag_file -o $patch.metadata.xml
        ../../bag2kmlbbox.py -o ${patch}-bbox.kml $bag_file

        bag_too_large.py -f $bag_file -m 10000
        if [ 1 == $? ]; then
           echo "WARNING: Skipping $patch.bag slow command because file too large"
           echo "The thumbs will be broken and the web page will not have the required images"
        else
            # Okay to generate a tif and do other stuff
            # EvenR suggested "-dstnodata 0" to help with the hillshade.
            # or gdal_translate -a_nodata -1 H11296_5m-depths-f32.tif H11296_5m-depths-f32-with-nodata.tif
            # But that did not work for me.
            gdalwarp -ot Float32 -t_srs EPSG:4326  $bag_file ${patch}-depths-f32.tif
            echo "FIX: make the color-relief use a ramp that is specific to each patch with gmt and cpt"
            gdaldem color-relief ${patch}-depths-f32.tif ../../color_ramp_fixed.dat  ${patch}-color-relief.tif -alpha -co ALPHA=YES
            gdaldem hillshade ${patch}-depths-f32.tif $patch-hillshade.tif 
            ../../gdal_copy_transparency.py -c ${patch}-color-relief.tif -H $patch-hillshade.tif -o $patch-hillshade-alpha.tif
            composite -blend 50 $patch-hillshade-alpha.tif ${patch}-color-relief.tif ${patch}-blend.tif # 2&> /dev/null

            echo
            echo "Correcting georeferencing..."
            listgeo -tfw ${patch}-depths-f32.tif
            geotifcp -e ${patch}-depths-f32.tfw ${patch}-blend.tif ${patch}.tif 

            convert ${patch}-blend.tif ${patch}.jpg
            convert -resize 200x200 ${patch}-blend.tif ${patch}-thumb-tmp.jpg 
            convert -border 2x2x2x2 -bordercolor black ${patch}-thumb-tmp.jpg ${patch}-thumb.jpg

            # --zoom=10-12 
            gdal2tiles.py26 -k -s EPSG:4326 ${patch}.tif
            mv $patch/doc.kml $patch/${patch}-bathy.kml

            #echo "bag_kml_popup.py: ..."
            echo ../../bag_kml_popup.py  -b $bag_file -s $survey -k ../../template.kml \
                -u http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/${survey}/ \
                -v -o $patch.kml
            ../../bag_kml_popup.py  -b $bag_file -s $survey -k ../../template.kml \
                -u http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/${survey}/ \
                -v -o $patch.kml
            convert -resize 200x200 ${patch}-hist.png ${patch}-hist-thumb-tmp.jpg
            convert -border 2x2x2x2 -bordercolor black ${patch}-hist-thumb-tmp.jpg ${patch}-hist-thumb.jpg
            convert ${patch}-hist.png ${patch}-hist.jpg

        fi
        # Back to non-tif requiring items

        mv ${patch}.tif ..
        # Cleanup
        rm -f ${patch}-hist.png
        rm -f ${patch}*-tmp.{jpg,png}
        rm -f *.{tif,tfw} *aux.xml

        # --dry-run
        #(cd .. && rsync --exclude-from=../rsync.excludes --verbose --progress --stats -r $survey  nrwais1.schwehr.org:www/bags/H10001-H12000/ )
    popd

    echo
    echo
    echo sleeping to keep the laptop from overheating too badly
    sleep 10

#fi # temp!!! FIX: remove

done

