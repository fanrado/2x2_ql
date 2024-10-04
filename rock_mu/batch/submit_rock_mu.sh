#!/bin/bash
# Runs proto_nd_flow on an example file.
# Before using this script, use
# >> source get_proto_nd_input.sh
# to download all the necessary inputs into the correct directories

# https://stackoverflow.com/a/66461030
chars='abcdefghijklmnopqrstuvwxyz'
n=10

rndstr=
for ((i = 0; i < n; ++i)); do
    rndstr+=${chars:RANDOM%${#chars}:1}
    # alternatively, str=$str${chars:RANDOM%${#chars}:1} also possible
done

StartDir="${PWD}"

cd $SCRATCH
if [[ ! -d rock_mu_sub ]]; then
    mkdir rock_mu_sub
fi
cd rock_mu_sub
echo $PWD

WorkDirParent="$SCRATCH/rock_mu_sub"
WorkDir="${WorkDirParent}/Dir${rndstr}"
if [[ ! -d ${WorkDir} ]]; then
    mkdir $WorkDir
fi
cd $WorkDir

git clone https://github.com/yszhang95/ndlar_flow.git -b feature_rock_mu_on_data

echo "Changing working directory to ${PWD}/ndlar_flow"
cd ndlar_flow
WORKFLOW6='yamls/proto_nd_flow/workflows/rock_muon_selection.yaml'


echo "Preparing python environment"
module load python
conda activate h5pyenv

INPUT_FILE=$1

OUTPUT_DIR="$SCRATCH/rock_mu_sub/output" #!!! change me

OUTPUT_NAME=(${INPUT_FILE//"/"/ })
OUTPUT_NAME=${OUTPUT_NAME[-1]}
OUTPUT_FILE="${OUTPUT_DIR}/${OUTPUT_NAME}"
OUTPUT_FILE=${OUTPUT_FILE//.hdf5/.rock_mu.h5}

if [[ ! -d $OUTPUT_DIR ]]; then
    mkdir $OUTPUT_DIR
fi

slconfig="prepare_env_${rndstr}.sl"
cat << _EOF_ > ${slconfig}
#!/bin/bash
#SBATCH -J rock_mu
#SBATCH -t 01:30:00
#SBATCH -N 1
#SBATCH -q debug
#SBATCH -C cpu
#SBATCH --account dune
#SBATCH --licenses=cfs,SCRATCH

srun -n32 --cpu_bind=cores h5flow  -c $WORKFLOW6 -i $INPUT_FILE -o $OUTPUT_FILE

echo "Done!"
echo "Output can be found at $OUTPUT_FILE"

# Other commands needed after srun, such as copy your output filies,
# should still be included in the Slurm script.
# cp <my_output_file> <target_location>/.
cp slurm-*.out ${WorkDirParent}
cp. $slconfig ${WorkDirParent}
_EOF_

# Now submit the batch job

sbatch ${slconfig}
# h5flow  -c $WORKFLOW6 -i $INPUT_FILE -o $OUTPUT_FILE
