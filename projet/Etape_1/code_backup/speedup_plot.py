import pandas as pd
import glob
import os
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Folder containing all your .csv files
FOLDER_PATH = "./logs/*.csv"

# Column name to base speedup on (e.g., "update_time" or "total_time").
TIME_COLUMN = "update_time"

# Output folder for plots
OUTPUT_FOLDER = "./plots"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_data_from_file(csv_file):
    """Extract thread count and timing data from a CSV file."""
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    
    # Find the "OpenMP threads: <value>" line
    thread_count = None
    for line in lines:
        if line.strip().startswith("OpenMP threads:"):
            try:
                thread_count = int(line.strip().split(":")[1])
                break
            except ValueError:
                print(f"Could not parse thread count in file {csv_file}")
                return None, None
    
    if thread_count is None:
        print(f"No thread count found in {csv_file}, skipping.")
        return None, None
    
    # Identify where the CSV portion starts
    data_start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("step,"):
            data_start_idx = i
            break
    
    if data_start_idx is None:
        print(f"No CSV header found in {csv_file}, skipping.")
        return None, None

    # Extract the CSV portion and parse into a DataFrame
    csv_data = lines[data_start_idx:]
    try:
        df = pd.read_csv(StringIO("".join(csv_data)))
    except Exception as e:
        print(f"Error parsing CSV data in {csv_file}: {e}")
        return None, None
    
    if TIME_COLUMN not in df.columns:
        print(f"Column '{TIME_COLUMN}' not found in {csv_file}. Skipping.")
        return None, None
    
    if "step" not in df.columns:
        print(f"No 'step' column found in {csv_file}. Skipping.")
        return None, None

    # Only keep 'step' and the chosen time column
    df = df[["step", TIME_COLUMN]].copy()
    df.rename(columns={TIME_COLUMN: "time"}, inplace=True)
    
    return thread_count, df

def group_data_by_thread_count():
    """Group all CSV files by thread count and return a dictionary of lists."""
    csv_files = glob.glob(FOLDER_PATH)
    
    if not csv_files:
        print(f"No CSV files found in {FOLDER_PATH}")
        return {}
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Dictionary to store data for each thread count
    data_by_thread_list = defaultdict(list)
    
    for csv_file in csv_files:
        thread_count, df = extract_data_from_file(csv_file)
        if thread_count is not None and df is not None:
            data_by_thread_list[thread_count].append(df)
            print(f"Processed {csv_file} - Thread count: {thread_count}")
    
    return data_by_thread_list

def calculate_average_data(data_by_thread_list):
    """Calculate average measurements for each thread count."""
    average_data_by_thread = {}
    
    for thread_count, df_list in data_by_thread_list.items():
        if not df_list:
            continue
        
        # Find the maximum step that appears in all dataframes
        min_max_step = min(df['step'].max() for df in df_list)
        
        # Filter dataframes to include only steps up to min_max_step
        filtered_dfs = [df[df['step'] <= min_max_step] for df in df_list]
        
        # Create a new DataFrame for the average values
        avg_df = pd.DataFrame()
        avg_df['step'] = filtered_dfs[0]['step']  # Use steps from the first DataFrame
        
        # Calculate average time for each step
        avg_df['time'] = pd.concat([df['time'] for df in filtered_dfs], axis=1).mean(axis=1)
        
        # Store the average DataFrame
        average_data_by_thread[thread_count] = avg_df
        
        print(f"Calculated average for {thread_count} threads based on {len(df_list)} files")
    
    return average_data_by_thread

def plot_step_by_step_speedup(average_data_by_thread):
    """Plot speedup vs. step for each thread count."""
    if 1 not in average_data_by_thread:
        print("No single-thread (thread_count=1) data found; cannot compute speedup.")
        return
    
    single_thread_df = average_data_by_thread[1].copy()
    single_thread_df.rename(columns={"time": "time_1"}, inplace=True)
    
    plt.figure(figsize=(12, 8))
    
    # Use a colormap for better distinction between lines
    colors = plt.cm.viridis(np.linspace(0, 1, len(average_data_by_thread) - 1))
    color_idx = 0
    
    for t, df_t in sorted(average_data_by_thread.items()):
        if t == 1:
            continue
        
        # Merge on 'step' so we line up times for the same step
        merged = pd.merge(single_thread_df, df_t, on="step", how="inner")
        
        # Compute speedup = time_1 / time
        merged["speedup"] = merged["time_1"] / merged["time"]
        
        # Plot speedup vs. step
        plt.plot(merged["step"], merged["speedup"], 
                 label=f"{t} threads", 
                 color=colors[color_idx],
                 linewidth=2)
        color_idx += 1
    
    # Add a horizontal red dashed line at y=1 to indicate the baseline
    plt.axhline(y=1, color='red', linestyle='--', label='Baseline (1×)')
    
    # Add a horizontal line at y=t for each thread count t
    for t in sorted(average_data_by_thread.keys()):
        if t > 1:
            plt.axhline(y=t, color='gray', linestyle=':', alpha=0.5)
    

    
    plt.xlabel("Step")
    plt.ylabel("Speedup")
    plt.title(f"Average Speedup vs. Step (based on {TIME_COLUMN})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

        # Optionally adjust y-limits so that 1 is centered in the plot:
    ylim = plt.ylim()
    span = max(1 - ylim[0], ylim[1] - 1)
    plt.ylim(0,2)

    output_file = os.path.join(OUTPUT_FOLDER, "avg_speedup_vs_step.png")
    plt.savefig(output_file)
    plt.show(block=False)
    print(f"Saved step-by-step speedup plot to {output_file}")

def plot_total_speedup(average_data_by_thread):
    """Plot total speedup as a bar chart."""
    if 1 not in average_data_by_thread:
        print("No single-thread (thread_count=1) data found; cannot compute speedup.")
        return
    
    single_thread_df = average_data_by_thread[1].copy()
    
    # Compute the 25th and 75th percentiles of the step values
    proportional_start = int(single_thread_df["step"].quantile(0.4))
    proportional_end = int(single_thread_df["step"].quantile(0.6))
    
    # Filter the DataFrame using these dynamic values
    single_thread_middle = single_thread_df[
        (single_thread_df["step"] >= proportional_start) & 
        (single_thread_df["step"] <= proportional_end)
    ]
    
    # Dictionary to store total speedup per thread
    total_speedup = {}
    speedup_std_dev = {}  # Standard deviation for error bars
    
    for t, df_t in sorted(average_data_by_thread.items()):
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
        total_speedup[t] = single_thread_middle["time"].sum() / total_time_t if total_time_t > 0 else 0
    
    # Now plot this total speedup as a bar chart
    plt.figure(figsize=(10, 6))
    threads = list(total_speedup.keys())
    speedups = [total_speedup[t] for t in threads]
    
    # Use a colormap for the bars
    colors = plt.cm.viridis(np.linspace(0, 1, len(threads)))
    
    bars = plt.bar(threads, speedups, color=colors)
        
    # Add the red baseline at y=1
    plt.axhline(y=1, color='red', linestyle='--', label='Baseline (1×)')
    
    # Add values on top of each bar
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 f'{height:.2f}×',
                 ha='center', va='bottom')
    
    ylim = plt.ylim()
    span = max(1 - ylim[0], ylim[1] - 1)
    plt.ylim(1 - span, 1 + span)
    
    plt.xlabel("Thread Count")
    plt.ylabel("Total Speedup")
    plt.title(f"Average Total Speedup (steps {proportional_start}–{proportional_end}, based on {TIME_COLUMN})")
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    output_file = os.path.join(OUTPUT_FOLDER, "avg_total_speedup.png")
    plt.savefig(output_file)
    plt.show(block=False)
    print(f"Saved total speedup plot to {output_file}")

def plot_efficiency(average_data_by_thread):
    """Plot parallel efficiency as a bar chart."""
    if 1 not in average_data_by_thread:
        print("No single-thread (thread_count=1) data found; cannot compute efficiency.")
        return
    
    single_thread_df = average_data_by_thread[1].copy()
    
    proportional_start = int(single_thread_df["step"].quantile(0.4))
    proportional_end = int(single_thread_df["step"].quantile(0.6))
    
    single_thread_middle = single_thread_df[
        (single_thread_df["step"] >= proportional_start) & 
        (single_thread_df["step"] <= proportional_end)
    ]
    
    # Dictionary to store efficiency per thread
    efficiency = {}
    
    for t, df_t in sorted(average_data_by_thread.items()):
        if t == 1:
            continue
        
        # Filter the DataFrame for the same proportional step range
        df_t_middle = df_t[
            (df_t["step"] >= proportional_start) & 
            (df_t["step"] <= proportional_end)
        ]
        
        # Sum the times over the filtered range
        total_time_t = df_t_middle["time"].sum()
        
        # Compute speedup = single-thread time sum / time sum for t threads
        speedup = single_thread_middle["time"].sum() / total_time_t if total_time_t > 0 else 0
        
        # Compute efficiency = speedup / thread count
        efficiency[t] = speedup / t
    
    # Now plot this efficiency as a bar chart
    plt.figure(figsize=(10, 6))
    threads = list(efficiency.keys())
    efficiencies = [efficiency[t] for t in threads]
    
    # Use a colormap for the bars
    colors = plt.cm.viridis(np.linspace(0, 1, len(threads)))
    
    bars = plt.bar(threads, efficiencies, color=colors)
    
    # Add the perfect efficiency line (y = 1)
    plt.axhline(y=1, color='red', linestyle='--', label='Perfect efficiency (100%)')
    
    # Add percentage values on top of each bar
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 f'{height*100:.1f}%',
                 ha='center', va='bottom')
    
    # Set the y-axis to start from 0 and end at 1.1
    plt.ylim(0, 1.1)
    
    plt.xlabel("Thread Count")
    plt.ylabel("Parallel Efficiency")
    plt.title(f"Average Parallel Efficiency (steps {proportional_start}–{proportional_end}, based on {TIME_COLUMN})")
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    output_file = os.path.join(OUTPUT_FOLDER, "avg_efficiency.png")
    plt.savefig(output_file)
    plt.show(block=False)
    print(f"Saved efficiency plot to {output_file}")

def main():
    # Group data by thread count
    data_by_thread_list = group_data_by_thread_count()
    
    if not data_by_thread_list:
        print("No valid data found. Exiting.")
        return
    
    # Calculate average data for each thread count
    average_data_by_thread = calculate_average_data(data_by_thread_list)
    
    # Plot the results
    plot_step_by_step_speedup(average_data_by_thread)
    plot_total_speedup(average_data_by_thread)
    #plot_efficiency(average_data_by_thread)
    
    print(f"All plots saved to {OUTPUT_FOLDER}")

if __name__ == "__main__":
    main()