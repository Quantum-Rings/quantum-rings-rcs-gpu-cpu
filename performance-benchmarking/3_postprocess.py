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
                        "duration_sec": task["duration_sec"]
                    })
        except Exception as e:
            print(f"⚠️ Skipping {json_file} due to error: {e}")

    # Sort rows by start time (converted to datetime for proper sort)
    rows.sort(key=lambda row: datetime.fromisoformat(row["start"].replace("Z", "")))

    with open(CSV_OUTPUT, "w", newline="") as csvfile:
        fieldnames = ["job_id", "task_id", "task_type", "start", "end", "duration_sec"]
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
    """
    Analyze the timing data and export a combined summary CSV for Overleaf.
    Metrics:
    - State Calc (First Shot Overall)
    - Queue (delay between first shot end and subsequent shots start)
    - Sampling (Subsequent Shots Overall durations)
    """

    import pandas as pd
    from datetime import timedelta

    df = pd.read_csv(csv_path)
    df["start_dt"] = pd.to_datetime(df["start"])
    df["end_dt"] = pd.to_datetime(df["end"])

    print("\n📊 Postprocess Summary")
    print("----------------------")

    # === First Shot Overall stats ===
    first_shot = df[df["task_type"] == "First Shot Overall"]

    if not first_shot.empty:
        first_shot_min = first_shot["duration_sec"].min()
        first_shot_max = first_shot["duration_sec"].max()
        first_shot_avg = first_shot["duration_sec"].mean()

        print(f"🛫 First Shot Overall:")
        print(f"   ↳ Min: {first_shot_min:.4f} sec")
        print(f"   ↳ Max: {first_shot_max:.4f} sec")
        print(f"   ↳ Avg: {first_shot_avg:.4f} sec")
    else:
        print("⚠️ No 'First Shot Overall' entries found.")
        first_shot_min = first_shot_max = first_shot_avg = 0

    print("")

    # === Subsequent Shots Overall stats ===
    subs = df[df["task_type"] == "Subsequent Shots Overall"]

    if not subs.empty:
        subs_min_duration = subs["duration_sec"].min()
        subs_max_duration = subs["duration_sec"].max()
        subs_avg_duration = subs["duration_sec"].mean()

        print(f"🎯 Measurements (Subsequent Shots Overall):")
        print(f"   ↳ Min Duration: {subs_min_duration:.4f} sec")
        print(f"   ↳ Max Duration: {subs_max_duration:.4f} sec")
        print(f"   ↳ Avg Duration: {subs_avg_duration:.4f} sec")
    else:
        print("⚠️ No 'Subsequent Shots Overall' entries found.")
        subs_min_duration = subs_max_duration = subs_avg_duration = 0

    print("")

    # === Delay between First Shot End and Subsequent Shots Start ===
    if not first_shot.empty and not subs.empty:
        first_shot_end = first_shot["end_dt"].min()
        subs["delay_from_first_shot_sec"] = (subs["start_dt"] - first_shot_end).dt.total_seconds()

        delay_min = subs["delay_from_first_shot_sec"].min()
        delay_max = subs["delay_from_first_shot_sec"].max()
        delay_avg = subs["delay_from_first_shot_sec"].mean()

        print(f"⏱️ Delay between First Shot and Subsequent Measurements:")
        print(f"   ↳ Min Delay: {delay_min:.4f} sec")
        print(f"   ↳ Max Delay: {delay_max:.4f} sec")
        print(f"   ↳ Avg Delay: {delay_avg:.4f} sec")
    else:
        print("⚠️ Cannot compute delays (missing First Shot or Subsequent Shots data).")
        delay_min = delay_max = delay_avg = 0

    print("")

    # === Export Combined Table for Overleaf ===
    combined_df = pd.DataFrame({
        "Metric": ["State Calc", "Queue", "Sampling"],
        "Min (sec)": [round(first_shot_min), round(delay_min), round(subs_min_duration)],
        "Max (sec)": [round(first_shot_max), round(delay_max), round(subs_max_duration)],
        "Avg (sec)": [round(first_shot_avg), round(delay_avg), round(subs_avg_duration)]
    })

    combined_df.to_csv("logs/job_stats_summary.csv", index=False)
    print(f"📄 Exported combined job stats summary to job_stats_summary.csv")


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


