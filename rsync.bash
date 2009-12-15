#!/bin/bash  -e

set -x # Turn on Debugging
# Just do the rsync

#for compressed_file in `find ./H10001-H12000/ -name \*.bag.gz`; do 
cd processed
for survey in *; do
    if [ -d $survey ]; then
        rsync --exclude-from=../rsync.excludes --verbose --progress --stats -r $survey  nrwais1.schwehr.org:www/bags/H10001-H12000/
    else
        echo not a survey
    fi

    echo sleeping ...
    sleep 2
done

