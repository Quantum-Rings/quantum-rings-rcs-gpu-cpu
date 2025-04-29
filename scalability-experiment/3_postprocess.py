import sys
import json
import csv
from pathlib import Path
from shared import GLOBAL_VARS
from datetime import datetime, timedelta

LOGS_DIR = Path(GLOBAL_VARS["logs_dir"])
CSV_OUTPUT = LOGS_DIR / "task_timings_summary.csv"
AMPLITUDE_OUTPUT = LOGS_DIR / "qr_amplitudes_combined.txt"

# Redirect print output to a file as well as stdout
class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w", buffering=1)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Start logging
sys.stdout = Logger("logs/postprocess_output.txt")

def collect_timings_to_csv():
    json_files = sorted(LOGS_DIR.glob("*.json"))
    
    rows = []

    for json_file in json_files:
        try:
            with open(json_file) as f:
                data = json.load(f)
                job_id = data.get("slurm", {}).get("job_id", "unknown")
                task_id = data.get("slurm", {}).get("task_id", "unknown")
                for task in data.get("tasks", []):
                    rows.append({
                        "job_id": job_id,
                        "task_id": task_id,
                        "task_type": task["task_type"],
                        "start": task["start"],
                        "end": task["end"],
                        "duration_sec": task["duration_sec"],
                        "shots": task.get("metadata", {}).get("shots", None)  # New: pull shots if present

                    })
        except Exception as e:
            print(f"⚠️ Skipping {json_file} due to error: {e}")

    # Sort rows by start time (converted to datetime for proper sort)
    rows.sort(key=lambda row: datetime.fromisoformat(row["start"].replace("Z", "")))

    with open(CSV_OUTPUT, "w", newline="") as csvfile:
        fieldnames = ["job_id", "task_id", "task_type", "start", "end", "duration_sec", "shots"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Wrote summary CSV to {CSV_OUTPUT}")

def combine_amplitude_logs():
    combined_lines = []
    pattern = "qr_amplitudes_circuit_*.txt"

    files = sorted(LOGS_DIR.glob(pattern))
    if not files:
        print(f"⚠️ No files found matching {pattern} in {LOGS_DIR}")
        return

    for file in files:
        with open(file) as f:
            combined_lines.extend(f.readlines())

    with open(AMPLITUDE_OUTPUT, "w") as out:
        out.writelines(combined_lines)

    print(f"✅ Combined {len(files)} files into {AMPLITUDE_OUTPUT}")

def format_duration(seconds):
    return str(timedelta(seconds=round(seconds, 3)))

def analyze_and_print(csv_path):
    import pandas as pd

    df = pd.read_csv(csv_path)
    df["start_dt"] = pd.to_datetime(df["start"])
    df["end_dt"] = pd.to_datetime(df["end"])

    earliest_start = df["start_dt"].min()
    latest_end = df["end_dt"].max()
    total_duration = (latest_end - earliest_start).total_seconds()

    # First and subsequent groups
    first_shot = df[df["task_type"] == "First Shot Overall"]
    subsequent = df[df["task_type"] == "Subsequent Shots Overall"]

    first_shot_end = first_shot["end_dt"].min()

    # Time gap from first shot end to each subsequent shot start
    subsequent["delay_from_first_shot_sec"] = (subsequent["start_dt"] - first_shot_end).dt.total_seconds()

    # Stats
    turnaround_times = subsequent["delay_from_first_shot_sec"]
    durations = subsequent["duration_sec"]

    print("\n📊 Postprocess Summary")
    print("----------------------")
    print(f"🕐  Earliest start time:      {earliest_start}")
    print(f"⌛  Latest end time:          {latest_end}")
    print(f"🧮  Total duration:           {total_duration:.4f} sec")
    print(f"                              {format_duration(total_duration)}")

    print(f"\n🚀  Turnaround time (first to earliest sub):")
    turnaround = (subsequent["start_dt"].min() - first_shot_end).total_seconds()
    print(f"   ↳ First Sub Start - First Shot End: {turnaround:.4f} sec")
    print(f"                                     | {format_duration(turnaround)}")

    print(f"\n📊 Subsequent Shot Execution Durations:")
    print(f"   ↳ Min: {durations.min():.4f} sec  | {format_duration(durations.min())}")
    print(f"   ↳ Max: {durations.max():.4f} sec  | {format_duration(durations.max())}")
    print(f"   ↳ Avg: {durations.mean():.4f} sec  | {format_duration(durations.mean())}")

    print(f"\n⏱️  Delay After First Shot (Start of Subsequent Jobs):")
    print(f"   ↳ Min: {turnaround_times.min():.4f} sec  | {format_duration(turnaround_times.min())}")
    print(f"   ↳ Max: {turnaround_times.max():.4f} sec  | {format_duration(turnaround_times.max())}")
    print(f"   ↳ Avg: {turnaround_times.mean():.4f} sec  | {format_duration(turnaround_times.mean())}")

    # === Build Jobs vs Shots per Job Table from actual logged data ===
    if not subsequent.empty:
        group = subsequent.groupby("shots").agg(
            Jobs=("job_id", "count"),
            ShotsPerJob=("shots", "first"),
            SamplingTimeSec=("duration_sec", "mean")
        ).reset_index(drop=True)

        shots = group["ShotsPerJob"].astype(int)
        jobs = 2500000 / shots
        group["Jobs"] = jobs
        group["ShotsPerJob"] = shots
        group["SamplingTimeSec"] = group["SamplingTimeSec"].round(1)

        group = group[["Jobs", "ShotsPerJob", "SamplingTimeSec"]]

        group.to_csv("logs/shots_vs_jobs_summary.csv", index=False)
        print(f"📄 Exported updated shots vs jobs table to shots_vs_jobs_summary.csv")


def process_amplitude_file (filename) -> (dict, dict, int) :
    input_file = open(filename, 'r')
    
    measfreq = {}
    measampl = {}
    
    # Using for loop
    for line in input_file:
        items = line.strip().split()
        # Access the three items
        item1, item2, item3 = items[0], items[1], items[2]
        Y = complex(float(item2), float(item3))
        YY = abs(Y)**2
        
        if item1 not in measfreq:
            measfreq[item1] = 0
            measampl[item1] = YY
        measfreq[item1] += 1
    
    # Close input file
    input_file.close()

    first_key = next(iter(measfreq))
    
    return measfreq,  measampl, len(first_key)

def f_xeb(counts, probs, n) ->float :
    
    total_samples = 0
    avg_prob = 0

    for key, val in counts.items():
        avg_prob += counts[key] * probs[key]
        total_samples += counts[key]

    calc_f_xeb = ((2**n) * (avg_prob / total_samples) )   - 1
    
    return calc_f_xeb

if __name__ == "__main__":
    collect_timings_to_csv()
    combine_amplitude_logs()

    wordfreq, wordampl, numberofqubits = process_amplitude_file(AMPLITUDE_OUTPUT)
    qr_xeb = f_xeb(wordfreq, wordampl, numberofqubits)
    print("QuantumRings f_xeb: ", qr_xeb, flush=True); 

    analyze_and_print(CSV_OUTPUT)


