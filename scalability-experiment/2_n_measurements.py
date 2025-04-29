from platform import python_version
print("Python Version:", python_version())

import os

from QuantumRingsLib import QuantumCircuit
from QuantumRingsLib import QuantumRingsProvider
from QuantumRingsLib import job_monitor
  
from shared import GLOBAL_VARS, get_paths, get_provider
from job_tracker import JobTracker 

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--shots", type=int, required=True)
args = parser.parse_args()

number_of_shots = args.shots

tracker = JobTracker()


with tracker.task("Subsequent Shots Overall", metadata={"shots": number_of_shots}):

    qasm_path, log_path, state_path = get_paths(53)
    provider = get_provider()

    # Obtain the backend for CPU.
    #                        ^^^
    backend = provider.get_backend("scarlet_quantum_rings")
    print(backend)

    if os.path.exists(log_path):
        os.remove(log_path)

    with tracker.task("Loading State"):
        qc1 =  QuantumCircuit(simulation_state_file = state_path)
        qc1.measure_all()

    with tracker.task("Subsequent Shots"):
        job = backend.run(qc1, shots=number_of_shots, mode="async", quiet=True, generate_amplitude = True, file = log_path)
        job_monitor(job, quiet=True)

tracker.write_json()
