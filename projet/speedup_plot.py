import pandas as pd
import glob
from io import StringIO
import matplotlib.pyplot as plt

# Folder containing all your .csv files
FOLDER_PATH = "./logs/*.csv"

# Column name to base speedup on (e.g., "update_time" or "total_time").
TIME_COLUMN = "update_time"

csv_files = glob.glob(FOLDER_PATH)

# Dictionary to store data for each thread count
data_by_thread = {}

for csv_file in csv_files:
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    # 1. Find the "OpenMP threads: <value>" line
    thread_count = None
    for line in lines:
        if line.strip().startswith("OpenMP threads:"):
            try:
                thread_count = int(line.strip().split(":")[1])
                break
            except ValueError:
                print(f"Could not parse thread count in file {csv_file}")
                break

    if thread_count is None:
        print(f"No thread count found in {csv_file}, skipping.")
        continue
    
    # 2. Identify where the CSV portion starts
    data_start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("step,"):
            data_start_idx = i
            break
    if data_start_idx is None:
        print(f"No CSV header found in {csv_file}, skipping.")
        continue

    # 3. Extract the CSV portion and parse into a DataFrame
    csv_data = lines[data_start_idx:]
    df = pd.read_csv(StringIO("".join(csv_data)))
    
    if TIME_COLUMN not in df.columns:
        print(f"Column '{TIME_COLUMN}' not found in {csv_file}. Skipping.")
        continue
    if "step" not in df.columns:
        print(f"No 'step' column found in {csv_file}. Skipping.")
        continue

    # Only keep 'step' and the chosen time column
    df = df[["step", TIME_COLUMN]].copy()
    df.rename(columns={TIME_COLUMN: "time"}, inplace=True)

    # Store this DataFrame in our dictionary
    data_by_thread[thread_count] = df

# We need a single-threaded run as the reference
if 1 not in data_by_thread:
    print("No single-thread (thread_count=1) data found; cannot compute speedup.")
    exit(0)

single_thread_df = data_by_thread[1].copy()
single_thread_df.rename(columns={"time": "time_1"}, inplace=True)

#
# Step-by-step Speedup Plot (using all steps)
#
plt.figure()  # Create a new figure for the step-by-step speedup

for t, df_t in sorted(data_by_thread.items()):
    if t == 1:
        continue
    
    # Merge on 'step' so we line up times for the same step
    merged = pd.merge(single_thread_df, df_t, on="step", how="inner")
    # merged has columns: ["step", "time_1", "time"]
    
    # Compute speedup = time_1 / time
    merged["speedup"] = merged["time_1"] / merged["time"]
    
    # Plot speedup vs. step
    plt.plot(merged["step"], merged["speedup"], label=f"{t} threads")

# Add a horizontal red dashed line at y=1 to indicate the baseline
plt.axhline(y=1, color='red', linestyle='--', label='Baseline (1×)')

# Optionally adjust y-limits so that 1 is centered in the plot:
ylim = plt.ylim()
span = max(1 - ylim[0], ylim[1] - 1)
plt.ylim(1 - span, 1 + span)

plt.xlabel("Step")
plt.ylabel("Speedup")
plt.title(f"Speedup vs. Step (based on {TIME_COLUMN})")
plt.legend()
plt.savefig("speedup_vs_step.png")
plt.show()

#
# Total Speedup Plot (filtering steps from proportional values)
#

# Dictionary to store total speedup per thread
total_speedup = {}

# Compute the 25th and 75th percentiles of the step values
proportional_start = int(single_thread_df["step"].quantile(0.4))
proportional_end = int(single_thread_df["step"].quantile(0.6))

# Filter the DataFrame using these dynamic values
single_thread_middle = single_thread_df[
    (single_thread_df["step"] >= proportional_start) & 
    (single_thread_df["step"] <= proportional_end)
]

for t, df_t in sorted(data_by_thread.items()):
    if t == 1:
        continue
    
    # Filter the DataFrame for the same proportional step range
    df_t_middle = df_t[
        (df_t["step"] >= proportional_start) & 
        (df_t["step"] <= proportional_end)
    ]
    
    # Sum the times over the filtered range
    total_time_t = df_t_middle["time"].sum()
    
    # Compute total speedup = single-thread time sum / time sum for t threads
    total_speedup[t] = single_thread_middle["time_1"].sum() / total_time_t if total_time_t > 0 else 0

# Now plot this total speedup as a bar chart
plt.figure()  # Create a new figure for the total speedup
threads = list(total_speedup.keys())
speedups = [total_speedup[t] for t in threads]

plt.bar(threads, speedups)

# Add the red baseline at y=1
plt.axhline(y=1, color='red', linestyle='--', label='Baseline (1×)')

# Adjust y-limits so that y=1 is centered (optional)
ylim = plt.ylim()
span = max(1 - ylim[0], ylim[1] - 1)
plt.ylim(1 - span, 1 + span)

plt.xlabel("Thread Count")
plt.ylabel("Total Speedup")
plt.title(f"Total Speedup (steps {proportional_start}–{proportional_end}, based on {TIME_COLUMN})")
plt.legend()
plt.savefig("total_speedup.png")
plt.show()
