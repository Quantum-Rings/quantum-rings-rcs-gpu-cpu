#!/bin/bash

# set execute permission on all scripts in the current directory and subdirectories
find . -name "*.sh" -exec chmod +x {} \;

#Load mamba
module load mamba/latest

#Cleanup if already implemented:
#mamba env remove -n quantumrings_gpu_exp

#Create a mamba environment in the user space, with python 3.11
mamba create -n quantumrings_gpu_exp python=3.11 pandas

#activate the new space, so we can install QuantumRingsLib into it.
source activate quantumrings_gpu_exp

#install Quantum Rings into it.
pip install quantumringslib-0.11.11-cp311-cp311-manylinux_2_27_x86_64.whl
pip install pandas

#Deactivate the space.  it will be available in the user space until removed. 
source deactivate

#In the future, we can publish this to the available environments so other users don't have to do this.
