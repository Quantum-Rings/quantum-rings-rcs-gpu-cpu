#!/bin/bash
#SBATCH --job-name=measurement
#SBATCH --output=logs/measurement_%j.out
#SBATCH --error=logs/measurement_%j.err
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8           # or as needed
#SBATCH -p htc ## Partition
#SBATCH -q public  ## QOS

# === Set up your environment (only if needed-- spawning seems to inherit this) ===
# Load mamba module if not already loaded
if ! command -v mamba &> /dev/null; then
    module load mamba/latest
fi

# Only activate env if it's not already active
if [[ "$CONDA_DEFAULT_ENV" != "quantumrings_gpu_exp" ]]; then
    source activate quantumrings_gpu_exp
fi

echo "Running measurement job index $JOB_INDEX with $SHOTS shots"

# Run your Python script
python 2_n_measurements.py --shots $SHOTS
