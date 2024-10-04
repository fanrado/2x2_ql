#!/bin/bash
# Runs proto_nd_flow on an example file.
# Before using this script, use
# >> source get_proto_nd_input.sh
# to download all the necessary inputs into the correct directories
#

python -c "from mpi4py import MPI; print('MPI Size is', MPI.COMM_WORLD.Get_size())"

# https://stackoverflow.com/a/66461030
chars='abcdefghijklmnopqrstuvwxyz'
n=10

rndstr=
for ((i = 0; i < n; ++i)); do
    rndstr+=${chars:RANDOM%${#chars}:1}
    # alternatively, str=$str${chars:RANDOM%${#chars}:1} also possible
done

WorkParentDir="$SCRATCH/rock_mu_scratch"
WorkDir="$SCRATCH/rock_mu_scratch/$rndstr"
echo $WorkDir
cd $WorkDir


echo

# 
INPUT_FILE=$1
# 
OUTPUT_DIR="$2/${rndstr}" #!!! change me

if [[ -d $OUTPUT_DIR ]]; then
    mkdir $OUTPUT_DIR
fi

OUTPUT_NAME=(${INPUT_FILE//"/"/ })
OUTPUT_NAME=${OUTPUT_NAME[-1]}
OUTPUT_FILE="${OUTPUT_DIR}/${OUTPUT_NAME}"
OUTPUT_FILE=${OUTPUT_FILE//.hdf5/.rock_mu.h5}
echo ${OUTPUT_FILE}
# 
# # for running on a login node
H5FLOW_CMD='h5flow'
# # for running on a single compute node with 32 cores
# #H5FLOW_CMD='srun -n32 h5flow'
# 
# # run all stages
WORKFLOW6='yamls/proto_nd_flow/workflows/rock_muon_selection.yaml'
# 
# # avoid being asked if we want to overwrite the file if it exists.
# # this is us answering "yes".
if [ -e $OUTPUT_FILE ]; then
   rm -i $OUTPUT_FILE
fi
# 
$H5FLOW_CMD -c $WORKFLOW6 -i $INPUT_FILE -o $OUTPUT_FILE
# 
echo "Done!"
echo "Output can be found at $OUTPUT_FILE"
# 
cd ../
rm -rf ndlar_flow
