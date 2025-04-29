#!/bin/bash

# === Configuration ===
STATE_PREP_WALL_TIME=${4:-00:30:00}       # Wall time for state preparation (job A)
STATE_PREP_PERFORMANCE=${5:-BalancedAccuracy}  # Performance setting (string)
# Example: array of shot counts per job (can be dynamically generated)
SHOTS_PER_JOB_ARRAY=(25000 10000 5000 2500)  # Replace this with your actual logic
CPU_WALL_TIME_ARRAY=("04:00:00" "02:00:00" "01:00:00" "01:00:00")

echo "=== Quantum Job Orchestration ==="
echo "State Prep:"
echo "  - Wall Time: $STATE_PREP_WALL_TIME"
echo "  - Performance: $STATE_PREP_PERFORMANCE"
echo "Measurements:"
echo "  - Shots: $SHOTS_PER_JOB_ARRAY"
echo "  - Wall Times: $CPU_WALL_TIME_ARRAY"
echo ""

# === Submit State Preparation ===
jid_a=$(sbatch --parsable \
  --time=$STATE_PREP_WALL_TIME \
  --export=ALL,PERFORMANCE="$STATE_PREP_PERFORMANCE" \
  run_prepare_state.sh)

echo "Submitted job A (State Prep): $jid_a"
echo ""


MEASUREMENT_JOB_COUNT=${#SHOTS_PER_JOB_ARRAY[@]}

for ((i = 0; i < MEASUREMENT_JOB_COUNT; i++)); do
  shots=${SHOTS_PER_JOB_ARRAY[$i]}
  walltime=${CPU_WALL_TIME_ARRAY[$i]}

  jid_b=$(sbatch --parsable \
    --dependency=afterok:$jid_a \
    --time=$walltime \
    --export=ALL,SHOTS=$shots,JOB_INDEX=$i \
    run_n_measurements.sh)

  echo "Submitted job $i: $jid_b (Shots: $shots)"
  b_job_ids+="$jid_b:"
done

# === Submit Post-Processing ===
# Trim trailing colon from job list
b_job_ids=${b_job_ids%:}

jid_c=$(sbatch --parsable \
  --dependency=afterok:$b_job_ids \
    --time=00:10:00 \
  run_postprocess.sh)

echo "Submitted job C (Post-Process): $jid_c"
