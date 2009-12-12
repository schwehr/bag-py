#!/usr/bin/env bash -e

set -x # Turn on Debugging

# Convert all BAGs from NGDC into KML visualizations

# /Volumes/KURT2009-1/BAGs/ngdc

#mkdir -p processed

#rm -f processed/*/*.{tif,grd}
#rm -f processed/*/*color*.{tif,grd}

#rm -rf processed

#for compressed_file in `find . -name \*.bag.gz`; do 
for compressed_file in H10001-H12000/H11334/BAG/H11334_5m.bag.gz; do
#for compressed_file in `cat bags.find`; do 
    echo "BAGcmp: $compressed_file"
    basename=`basename $compressed_file`
    echo "basename: $basename"
    src=`basename ${compressed_file%%.gz}`
    echo "BAG: $src"
    survey=`echo $compressed_file | cut -f2 -d/ `
    echo "survey: $survey"

    patch=${src%%.bag}
    echo "patch: $patch"

    mkdir -p processed/$survey
    gzcat $compressed_file > processed/$survey/$src
    pushd processed/$survey
        rm -f *.png *.tif *.jpg 
        echo Processing patch: $patch

        # Get the basic info references
        ~/local/bin/gdalinfo -hist $patch.bag > $patch.bag.info.txt
        
        ../../bag_xml_dump.py -b `pwd`/$patch.bag -o $patch.metadata.xml

        ~/local/bin/gdalwarp -ot Float32 -t_srs EPSG:4326  $patch.bag ${patch}-depths-f32.tif
        echo "FIX: make the color-relief use a ramp that is specific to each patch with gmt and cpt"
        ~/local/bin/gdaldem color-relief -co "nv=0" ${patch}-depths-f32.tif ../../color_ramp_fixed.dat  ${patch}-color-relief.tif -alpha
        ~/local/bin/gdaldem hillshade ${patch}-depths-f32.tif $patch-hillshade.tif 
        composite -blend 50 $patch-hillshade.tif ${patch}-color-relief.tif ${patch}-blend.tif # 2&> /dev/null

        echo
        echo "Correcting georeferencing..."
        listgeo -tfw ${patch}-depths-f32.tif
        geotifcp -e ${patch}-depths-f32.tfw ${patch}-blend.tif ${patch}.tif 
     
        #pwd
        #ls ../..
        cp ../../template.kml .
        #../../bag_kml_popup.py $patch
        echo "bag_kml_popup.py: ..."
        ../../bag_kml_popup.py  -b $patch.bag -s $survey -k ../../template.kml \
            -u http://nrwais1.schwehr.org/~schwehr/bags/H10001-H12000/${survey}/ \
            -v -o $patch.kml
        convert -resize 200x200 ${patch}-hist.png ${patch}-hist-thumb.jpg
        convert ${patch}-hist.png ${patch}-hist.jpg
        rm ${patch}-hist.png
        #convert -border 2x2x2x2 -bordercolor black ${patch}-hist-tmp.jpg ${patch}-hist-thumb.jpg
        rm -f template.kml

        convert ${patch}-blend.tif ${patch}.jpg
        convert -resize 200x200 ${patch}-blend.tif ${patch}-thumb-tmp.jpg 
        convert -border 2x2x2x2 -bordercolor black ${patch}-thumb-tmp.jpg ${patch}-thumb.jpg

        rm -f ${patch}-*-tmp.{jpg,png}

        gdal2tiles.py26 -k -s EPSG:4326 ${patch}.tif
        #ls -l $patch
        mv $patch/doc.kml $patch/${patch}-bathy.kml
        #rm -f *.{tif,tfw,bag} *aux.xml
        #(cd .. && scp -r $survey nrwais1:www/bags/H10001-H12000/)
        echo survey: $survey
        # --dry-run
        (cd .. && rsync --exclude-from=../rsync.excludes --verbose --progress --stats -r $survey  nrwais1.schwehr.org:www/bags/H10001-H12000/ )
    popd

    echo
    echo
done

