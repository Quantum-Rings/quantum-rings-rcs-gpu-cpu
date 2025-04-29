import sys
from platform import python_version
print("Python Version:", python_version())

from QuantumRingsLib import job_monitor
from QuantumRingsLib import OptimizeQuantumCircuit, QuantumCircuit
 
from shared import GLOBAL_VARS, get_paths, get_provider
from job_tracker import JobTracker 

import time

# Initialize JobTracker
tracker = JobTracker()

with tracker.task("First Shot Overall"):
    qasm_path, log_path, state_path = get_paths(53)
    provider = get_provider()

    # Obtain the backend for GPU.
    #                        ^^^
    backend = provider.get_backend("amber_quantum_rings")
    print(backend)

    # Perform only one shot.
    # Do not measure
    # After the circuit executes, save the Simulation State into a disk file

    number_of_shots = 1
 
    print("Circuit: ", qasm_path , "\nLog file: ", log_path, "\State file: ", state_path, flush=True)

    with tracker.task("Optimization"):
        qc = QuantumCircuit.from_qasm_file(qasm_path)
        OptimizeQuantumCircuit(qc)
        qc.count_ops()
            
    print("Circuit optimized. Sending for execution.", flush=True)

    with tracker.task("Execution (First Shot)"):
        #performance_setting = "BalancedAccuracy"
        #job = backend.run(qc, shots=number_of_shots, performance=performance_setting, mode="sync", quiet=True, generate_amplitude = False)
        job = backend.run(qc, shots=number_of_shots, mode="sync", quiet=True, generate_amplitude = False)
        job_monitor(job, quiet=True)
        result = job.result()

    with tracker.task("Write State"):
        result.SaveSystemStateToDiskFile(state_path)

tracker.write_json()
