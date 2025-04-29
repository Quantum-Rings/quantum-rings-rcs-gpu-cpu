import os
import json
import time
from pathlib import Path
from datetime import datetime
from platform import python_version

from shared import GLOBAL_VARS

class JobTracker:
    class Task:
        def __init__(self, task_type: str, tracker: "JobTracker"):
            self.task_type = task_type
            self.tracker = tracker
            self.start_time = None
            self.end_time = None

        def __enter__(self):
            self.start_time = time.time()
            self.tracker._write_log(f"START {self.task_type}")
            self.tracker.write_json()
            print(f"Starting task '{self.task_type}'")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.finish()
            self.tracker.tasks.append(self)
            duration = self.to_dict()["duration_sec"]
            self.tracker._write_log(f"FINISH {self.task_type}", {"duration": duration})
            self.tracker.write_json()
            print(f"Finished task '{self.task_type}' in {duration:.4f} seconds.")

        def finish(self):
            self.end_time = time.time()

        def to_dict(self):
            return {
                "task_type": self.task_type,
                "start": datetime.utcfromtimestamp(self.start_time).isoformat() + "Z",
                "end": datetime.utcfromtimestamp(self.end_time).isoformat() + "Z" if self.end_time else None,
                "duration_sec": round(self.end_time - self.start_time, 4) if self.end_time else None
            }

    def __init__(self, log_file_path: Path = None, json_file_path: Path = None):
        job_id = GLOBAL_VARS["job_id"]
        log_dir = Path(GLOBAL_VARS["logs_dir"])

        self.tasks = []

        self.log_file = log_file_path or (log_dir / f"{job_id}.log")
        self.json_file = json_file_path or (log_dir / f"{job_id}.json")

        self.slurm = {
            "job_id": os.getenv("SLURM_JOB_ID"),
            "task_id": os.getenv("SLURM_ARRAY_TASK_ID"),
            "node": os.getenv("SLURMD_NODENAME"),
        }

        self._write_log("START")

    def task(self, task_type: str):
        return self.Task(task_type, tracker=self)

    def _write_log(self, event_type: str, extra: dict = None):
        timestamp = datetime.utcnow().isoformat() + "Z"
        message = f"[{timestamp}] {event_type}"
        if extra:
            message += f" | {json.dumps(extra)}"

        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def write_json(self):
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "slurm": self.slurm,
            "python_version": python_version(),
            "tasks": [t.to_dict() for t in self.tasks]
        }
        with open(self.json_file, "w") as f:
            json.dump(record, f, indent=2)
