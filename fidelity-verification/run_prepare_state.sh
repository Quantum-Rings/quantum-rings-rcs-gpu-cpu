#!/bin/bash
#SBATCH --job-name=prepare_state
#SBATCH --output=logs/prepare_state_%j.out
#SBATCH --error=logs/prepare_state_%j.err
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4            # or as needed
#SBATCH --time=00:30:00              # or adjust based on how long it takes
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

python 1_prepare_state.py