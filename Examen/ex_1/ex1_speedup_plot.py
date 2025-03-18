import pandas as pd
import matplotlib.pyplot as plt
import glob
import re

# ------------------------------
# Read serial CSV file and separate rows
# ------------------------------
serial_filename = "original_time.csv"
df_serial = pd.read_csv(serial_filename)

# Get the serial total processing time (the row labeled "Total")
df_serial_total = df_serial[df_serial['Image'] == 'Total']
serial_total = float(df_serial_total['ProcessingTime'].values[0])

# Get per-image data (exclude the "Total" row)
df_serial_images = df_serial[df_serial['Image'] != 'Total']

# ------------------------------
# Find MPI CSV files (assumed to contain 'mpi' in their name)
# ------------------------------
mpi_files = glob.glob("*mpi*.csv")

# Lists to hold the number of processes, total times, and average per-image speedups
processes = []
global_times = []
avg_speedups = []

# Process each MPI file
for filename in mpi_files:
    # Extract number of processes from filename using regex (e.g., "1_mpi...", "2_mpi...", etc.)
    match = re.search(r"(\d+)_mpi", filename)
    if match:
        proc = int(match.group(1))
        
        # Read MPI CSV file
        df_mpi = pd.read_csv(filename)
        
        # Extract the total processing time from the "Total" row
        df_mpi_total = df_mpi[df_mpi['Image'] == 'Total']
        mpi_total = float(df_mpi_total['ProcessingTime'].values[0])
        
        # Get per-image rows (exclude the "Total" row)
        df_mpi_images = df_mpi[df_mpi['Image'] != 'Total']
        
        # Merge the serial and MPI per-image data on the image name
        merged = pd.merge(df_serial_images, df_mpi_images, on='Image', suffixes=('_serial', '_mpi'))
        
        # Compute the speedup for each image (serial time divided by MPI time)
        merged['speedup'] = merged['ProcessingTime_serial'] / merged['ProcessingTime_mpi']
        
        # Compute the average per-image speedup for this MPI run
        avg_speedup = merged['speedup'].mean()
        
        # Append the data
        processes.append(proc)
        global_times.append(mpi_total)
        avg_speedups.append(avg_speedup)

# Sort data by number of processes (in case file order is not sorted)
sorted_data = sorted(zip(processes, global_times, avg_speedups), key=lambda x: x[0])
processes, global_times, avg_speedups = zip(*sorted_data)

# ------------------------------
# Compute Global Speedup (using total processing times)
# ------------------------------
# Global speedup is defined as the ratio of serial total time to MPI total time.
global_speedups = [serial_total / t for t in global_times]

# ------------------------------
# Plot Average Per-Image Speedup
# ------------------------------
plt.figure()
plt.plot(processes, avg_speedups, marker='o', linestyle='-')
plt.xlabel('Number of Processes')
plt.ylabel('Average Per-Image Speedup')
plt.title('Average Per-Image Speedup vs Number of Processes')
plt.grid(True)
plt.savefig("average_speedup.png")  # Saves the figure to a file

# ------------------------------
# Plot Global Speedup with Ideal Speedup Curve
# ------------------------------
plt.figure()
plt.plot(processes, global_speedups, marker='o', linestyle='-', label='Global Speedup')
# Ideal speedup is assumed to be linear: ideal speedup = number of processes
plt.plot(processes, processes, marker='o', linestyle='--', label='Ideal Speedup')
plt.xlabel('Number of Processes')
plt.ylabel('Global Speedup (Total Serial Time / MPI Total Time)')
plt.title('Global Speedup vs Number of Processes')
plt.legend()
plt.grid(True)
plt.savefig("global_speedup.png")  # Saves the figure to a file

plt.show()
