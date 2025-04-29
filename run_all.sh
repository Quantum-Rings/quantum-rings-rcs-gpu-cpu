#!/bin/bash

echo "=== Running All Quantum Experiments ==="

cd performance-benchmarking
bash ./run_performance_exp.sh

cd ../scalability-experiment
bash ./run_scalability_exp.sh 

cd ../fidelity-verification
bash ./run_fidelity_exp.sh 

echo "=== All Experiments Submitted ==="
