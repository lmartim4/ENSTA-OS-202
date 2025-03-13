import pandas as pd
import glob
from io import StringIO
import matplotlib.pyplot as plt

# Folder containing all your .csv files
FOLDER_PATH = "./logs/*.csv"

# Column name to base speedup on (e.g., "update_time" or "total_time").
TIME_COLUMN = "update_time"

csv_files = glob.glob(FOLDER_PATH)

# Dictionary to store data for each thread count:
# data_by_thread[thread_count] = DataFrame with columns ["step", "time"]
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
    
    # We only need the "step" column and the chosen time column
    if TIME_COLUMN not in df.columns:
        print(f"Column '{TIME_COLUMN}' not found in {csv_file}. Skipping.")
        continue
    if "step" not in df.columns:
        print(f"No 'step' column found in {csv_file}. Skipping.")
        continue

    df = df[["step", TIME_COLUMN]].copy()
    # Rename the chosen column to "time" for consistency
    df.rename(columns={TIME_COLUMN: "time"}, inplace=True)

    # Store this DataFrame in our dictionary
    data_by_thread[thread_count] = df

# We need a single-threaded run as the reference
if 1 not in data_by_thread:
    print("No single-thread (thread_count=1) data found; cannot compute speedup.")
    exit(0)

single_thread_df = data_by_thread[1].copy()
single_thread_df.rename(columns={"time": "time_1"}, inplace=True)

plt.figure()  # Create a new figure

# For each thread count except 1, compute speedup vs. step
for t, df_t in sorted(data_by_thread.items()):
    if t == 1:
        continue
    
    # Merge on 'step' so we line up times for the same step
    merged = pd.merge(single_thread_df, df_t, on="step", how="inner")
    # merged has columns: ["step", "time_1", "time"] 
    # where "time_1" is single-thread time, "time" is multi-thread time
    
    # Compute speedup = time_1 / time
    merged["speedup"] = merged["time_1"] / merged["time"]
    
    # Plot speedup vs. step
    plt.plot(merged["step"], merged["speedup"], label=f"{t} threads")

plt.xlabel("Step")
plt.ylabel("Speedup")
plt.title(f"Speedup vs. Step (based on {TIME_COLUMN})")
plt.legend()


plt.savefig("speedup.png")
plt.show()