#!/usr/bin/env bash 
# -e

set -x # Turn on Debugging

# Convert all BAGs from NGDC into KML visualizations

# /Volumes/KURT2009-1/BAGs/ngdc

#mkdir -p processed

#rm -f processed/*/*.{tif,grd}
#rm -f processed/*/*color*.{tif,grd}

#rm -rf processed

PATH=`pwd`:$PATH

for compressed_file in `cat find.bag`; do 

#for compressed_file in `find ./H10001-H12000/ -name \*.bag.gz`; do 

#for compressed_file in `find . -name \*.bag.gz | head -1`; do 
#for compressed_file in H10001-H12000/H11334/BAG/H11334_5m.bag.gz; do
#for compressed_file in `cat bags.find`; do 
    echo "BAGcmp: $compressed_file"
    basename=`basename $compressed_file`
    echo "basename: $basename"
    src=`basename ${compressed_file%%.gz}`
    echo "BAG: $src"
    survey=`echo $compressed_file | cut -f3 -d/ `
    echo "survey: $survey"

    patch=${src%%.bag}
    echo "patch: $patch"

    mkdir -p processed/$survey
    gzcat $compressed_file > processed/$survey/$src
    pushd processed/$survey
        #rm -f *.png *.tif *.jpg 
        echo Processing patch: $patch

        # Get the basic info references
        ~/local/bin/gdalinfo -hist $patch.bag > $patch.bag.info.txt
        
        ../../bag_xml_dump.py -b `pwd`/$patch.bag -o $patch.metadata.xml

        ../../bag2kmlbbox.py -o ${patch}-bbox.kml $patch.bag

        echo "FIX: remove silly small bag size threshold"
        bag_too_large.py $patch.bag 5000
        if [ 1 == $? ]; then
           echo "WARNING: Skipping $patch.bag slow command because file too large"
           echo "The thumbs will be broken and the web page will not have the required images"
        else
            # Okay to generate a tif and do other stuff
            ~/local/bin/gdalwarp -ot Float32 -t_srs EPSG:4326  $patch.bag ${patch}-depths-f32.tif
            echo "FIX: make the color-relief use a ramp that is specific to each patch with gmt and cpt"
            ~/local/bin/gdaldem color-relief ${patch}-depths-f32.tif ../../color_ramp_fixed.dat  ${patch}-color-relief.tif -alpha -co ALPHA=YES
            ~/local/bin/gdaldem hillshade ${patch}-depths-f32.tif $patch-hillshade.tif 
            composite -blend 50 $patch-hillshade.tif ${patch}-color-relief.tif ${patch}-blend.tif # 2&> /dev/null

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

            echo "bag_kml_popup.py: ..."
            ../../bag_kml_popup.py  -b $patch.bag -s $survey -k ../../template.kml \
                -u http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/${survey}/ \
                -v -o $patch.kml
            convert -resize 200x200 ${patch}-hist.png ${patch}-hist-thumb-tmp.jpg
            convert -border 2x2x2x2 -bordercolor black ${patch}-hist-thumb-tmp.jpg ${patch}-hist-thumb.jpg
            convert ${patch}-hist.png ${patch}-hist.jpg

        fi
        # Back to non-tif requiring items


        # Cleanup
        #rm -f ${patch}-hist.png
        rm -f ${patch}*-tmp.{jpg,png}
        rm -f *.{tif,tfw} *aux.xml
        rm -f *.bag

        # --dry-run
        #(cd .. && rsync --exclude-from=../rsync.excludes --verbose --progress --stats -r $survey  nrwais1.schwehr.org:www/bags/H10001-H12000/ )
    popd

    echo
    echo
    echo sleeping to keep the laptop from overheating too badly
    sleep 10
done

