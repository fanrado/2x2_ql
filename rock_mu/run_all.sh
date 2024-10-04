#!/bin/bash

files=$(cat files.txt)
for f in ${files}; do
    # echo $(basename $f)
    python track_hist.py $f
done
