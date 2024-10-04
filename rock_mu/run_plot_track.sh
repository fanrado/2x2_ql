#!/bin/bash

files=$(cat files.txt)
for f in ${files}; do
    # echo $(basename $f)
    python plot_track2.py $f
done
