#!/bin/bash

# === Configuration ===
MEASUREMENT_JOB_COUNT=${1:-100}           # Number of B jobs
MEASUREMENT_TOTAL_SHOTS=${2:-2500000}       # Total shots to divide among B jobs
MEASUREMENT_WALL_TIME=${3:-04:00:00}      # Wall time for B jobs

# Good values for testing
#MEASUREMENT_JOB_COUNT=${1:-1}           # Number of B jobs
#MEASUREMENT_TOTAL_SHOTS=${2:-1000}       # Total shots to divide among B jobs
#MEASUREMENT_WALL_TIME=${3:-00:30:00}      # Wall time for B jobs

STATE_PREP_WALL_TIME=${4:-00:30:00}       # Wall time for state preparation (job A)
STATE_PREP_PERFORMANCE=${5:-BalancedAccuracy}  # Performance setting (string)

echo "=== Quantum Job Orchestration ==="
echo "State Prep:"
echo "  - Wall Time: $STATE_PREP_WALL_TIME"
echo "  - Performance: $STATE_PREP_PERFORMANCE"
echo "Measurements:"
echo "  - Job Count: $MEASUREMENT_JOB_COUNT"
echo "  - Total Shots: $MEASUREMENT_TOTAL_SHOTS"
echo "  - Wall Time: $MEASUREMENT_WALL_TIME"
echo ""

# === Submit State Preparation ===
jid_a=$(sbatch --parsable \
  --time=$STATE_PREP_WALL_TIME \
  --export=ALL,PERFORMANCE="$STATE_PREP_PERFORMANCE" \
  run_prepare_state.sh)

echo "Submitted job A (State Prep): $jid_a"
echo ""

# === Submit Measurement Jobs ===
b_job_ids=""
shots_per_job=$((MEASUREMENT_TOTAL_SHOTS / MEASUREMENT_JOB_COUNT))

for ((i = 0; i < MEASUREMENT_JOB_COUNT; i++)); do
  jid_b=$(sbatch --parsable \
    --dependency=afterok:$jid_a \
    --time=$MEASUREMENT_WALL_TIME \
    --export=ALL,SHOTS=$shots_per_job,JOB_INDEX=$i \
    run_n_measurements.sh)
  
  echo "Submitted job B[$i]: $jid_b (Shots: $shots_per_job)"
  b_job_ids+="$jid_b:"
done
echo ""

# === Submit Post-Processing ===
# Trim trailing colon from job list
b_job_ids=${b_job_ids%:}

jid_c=$(sbatch --parsable \
  --dependency=afterok:$b_job_ids \
    --time=00:10:00 \
  run_postprocess.sh)

echo "Submitted job C (Post-Process): $jid_c"
