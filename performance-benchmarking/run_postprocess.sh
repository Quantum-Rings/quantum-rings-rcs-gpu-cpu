#!/bin/bash
#SBATCH --job-name=postprocess
#SBATCH --output=logs/postprocess_%j.out
#SBATCH --error=logs/postprocess_%j.err
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4           # or as needed
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

echo "Postprocessing"

# Run your Python script
python 3_postprocess.py
