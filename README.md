# README.md

# Quantum-Rings RCS GPU/CPU Simulation Pipeline

This repository contains the full reproducibility artifacts for the SC'25 paper *"Revisiting Quantum Supremacy: Simulating Sycamore-Class Circuits Using Hybrid CPU/GPU HPC Workloads."*

It provides scripts, configurations, and instructions to reproduce:
- **Performance Benchmarking** (53-qubit, 20-cycle simulation)
- **Scalability Experiments** (linear scaling up to 1000 jobs)
- **Fidelity Verification** (53-qubit, 14-cycle XEB validation)

Artifacts for each experiment are organized into structured experiment directories under the `experiments/` subfolder.

---

## Quick Start

### 1. Setup Environment

```bash
bash onetime_setup_env.sh
```

- This creates a Mamba environment with Python 3.11, QuantumRingsLib, and Pandas.
- Safe to re-run if needed.

- This sets up the environment and runs all three experiments sequentially.

### 2. Hardware Requirements
- 1x NVIDIA A100 GPU (compute capability 8.6+, 32GB VRAM)
- CPU-only nodes (>= 8 cores, >= 16GB RAM per job)
- Shared file system accessible across nodes
- SLURM job scheduler

### 3. Run the Experiments

You can run all experiments, or run any individual experiment.  In either case, the output files will be stored in the a ```logs``` directory under the experiment.

To run all experiments, simply run:

```bash
bash run_all.sh
```

To run a specific experiment manually:

**Example: Performance Benchmarking**

```bash
cd experiments/performance-benchmarking
bash run_performance_exp.sh
```

This will:
- Build the quantum state with GPU (~6 minutes)
- Sample with 100 parallel CPU jobs
- Post-process outputs and compute runtime + XEB

### 4. Output Files

- Job logs: `logs/{SLURM_ID}.json`, `logs/{SLURM_ID}.log`
- Raw measurement files per job
- Consolidated measurement: `qr_amplitudes_combined.txt`
- Timing summary: `task_timings_summary.csv`
- XEB score printed to terminal and stored in postprocessing output

---

## Artifact Details

### A1: Performance Benchmarking
- Directory: `experiments/performance-benchmarking/`
- Related to Paper Section 5.2, Table 1

### A2: Scalability Analysis
- Directory: `experiments/scalability-experiment/`
- Related to Paper Section 5.3, Table 2, Figure 1
- Varies job counts (100, 250, 500, 1000)

### A3: Fidelity Verification
- Directory: `experiments/fidelity-verification/`
- Related to Paper Section 5.1

---

## Important Notes
- For optimal performance, experiments benefit from **reserved compute resources** to minimize queue delays.
- Sampling phase is highly parallelizable.
- All SLURM job dependencies are automatically handled by provided scripts.

---

## Citation

If you use this code, please cite:

```bibtex
@inproceedings{wold2025revisiting,
  title={Revisiting Quantum Supremacy: Simulating Sycamore-Class Circuits Using Hybrid CPU/GPU HPC Workloads},
  author={Wold, Bob and Kasirajan, Venkateswaran},
  booktitle={Proceedings of SC '25},
  year={2025},
  organization={ACM}
}
```

---

## Contact

- Bob Wold: [bob.wold@quantumrings.com](mailto:bob.wold@quantumrings.com)
- Venkat Kasirajan: [venkat.kasirajan@quantumrings.com](mailto:venkat.kasirajan@quantumrings.com)

---

**Let's keep pushing the boundaries of classical simulation.**

