#!/bin/bash
files=( packet-0050017-2024_07_08_15_03_34_CDT_hists.root packet-0050017-2024_07_08_15_13_35_CDT_hists.root packet-0050017-2024_07_08_15_23_37_CDT_hists.root packet-0050017-2024_07_08_15_33_38_CDT_hists.root packet-0050017-2024_07_08_15_43_39_CDT_hists.root packet-0050017-2024_07_08_15_53_40_CDT_hists.root )

for f in ${files[@]}; do
    python3 plot_profile.py $f
done
