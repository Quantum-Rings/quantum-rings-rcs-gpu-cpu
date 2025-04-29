import os
import json
import time
from pathlib import Path
from datetime import datetime
import fcntl
from platform import python_version

from QuantumRingsLib import QuantumRingsProvider

GLOBAL_VARS = {
    "logs_dir": "./logs/",
    "qasm_dir": "./qasm/",
    "state_dir": "./state/",
    "job_id": os.getenv("SLURM_JOB_ID"),
    "task_id": os.getenv("SLURM_ARRAY_TASK_ID"),
    "node": os.getenv("SLURMD_NODENAME"),
}


############## Helpers ##############
def get_paths(qubits: int):
    """
    Returns the full paths for the QASM file and the corresponding log file
    based on a qubit count. Verifies the QASM file exists.

    Args:
        qubits (int): Number of qubits (used in the QASM file name)

    Returns:
        tuple: (qasm_file_path: Path, log_file_path: Path)

    Raises:
        FileNotFoundError: If the QASM file does not exist
    """
    qasm_file_name = f"circuit_n{qubits}_m14_s0_e0_pEFGH.qasm"
    #qasm_file_name = f"circuit_n{qubits}_m20_s0_e0_pABCDCDAB.qasm"
    qasm_file_path = Path(GLOBAL_VARS["qasm_dir"]) / qasm_file_name
    log_file_path = Path(GLOBAL_VARS["logs_dir"]) / f"qr_amplitudes_{qasm_file_name[:-5]}_{GLOBAL_VARS['job_id']}.txt"
    state_file_path = Path(GLOBAL_VARS["state_dir"]) / f"qr_state_{qasm_file_name[:-5]}.bin"

    if not qasm_file_path.exists():
        raise FileNotFoundError(f"QASM file {qasm_file_path} does not exist. Please check.")

    return str(qasm_file_path), str(log_file_path), str(state_file_path)


def get_provider():

    # Obtain the Quantum Rings Provider
    provider = QuantumRingsProvider()

    # List all backends available
    provider.backends()

    #List the account
    print(provider.active_account())

    return provider