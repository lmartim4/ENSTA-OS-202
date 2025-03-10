import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import os

def extract_metadata_and_data(filename):
    """
    Extracts metadata (OpenMP threads) and timing data from a CSV file.
    """
    metadata = {}
    data_lines = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            
            if line.startswith("OpenMP threads:"):
                try:
                    metadata['OpenMP threads'] = int(line.split(':')[1].strip())
                except:
                    pass

            elif re.match(r'^\d+,\d+,\d+,\d+$', line):
                data_lines.append(line)
                
    if not data_lines:
        raise ValueError(f"No valid data found in the file {filename}.")
    
    df = pd.DataFrame(
        [x.split(',') for x in data_lines], 
        columns=['step', 'update_time', 'display_time', 'total_time']
    )
    
    df = df.astype({
        'step': int, 
        'update_time': int, 
        'display_time': int, 
        'total_time': int
    })
    
    return metadata, df
def collect_results_and_plot(folder_path='logs'):
    """
    Reads CSV files, extracts timing data, computes speedup and efficiency, and plots them.
    """
    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
    
    results = {}  # thread_count -> total_time
    
    for csv_file in csv_files:
        try:
            metadata, df = extract_metadata_and_data(csv_file)
            threads = metadata.get('OpenMP threads', None)
            if threads is None:
                continue
            
            total_time = df['total_time'].sum()
            results[threads] = total_time
        except Exception as e:
            print(f"Error with file {csv_file}: {e}")
    
    if not results:
        print("No valid results found. Exiting.")
        return
    
    sorted_results = sorted(results.items(), key=lambda x: x[0])
    baseline_threads = 1 if 1 in results else sorted_results[0][0]
    baseline_time = results[baseline_threads]
    
    thread_counts = []
    total_times = []
    speedups = []
    efficiencies = []
    
    for t, total_time in sorted_results:
        thread_counts.append(t)
        speedup = baseline_time / total_time
        speedups.append(speedup)
        efficiencies.append(speedup / t)
        total_times.append(total_time)

    # Speedup Plot
    plt.figure(figsize=(8, 5))
    plt.plot(thread_counts, speedups, marker='o', linestyle='-', color='blue', label='Measured Speedup')
    plt.xlabel('Number of OpenMP Threads')
    plt.ylabel('Speedup (T1 / Tn)')
    plt.title('Speedup vs. Number of Threads')
    plt.legend()
    plt.grid(True)
    plt.show(block=False)

    # Efficiency Plot (Speedup / Threads)
    plt.figure(figsize=(8, 5))
    plt.plot(thread_counts, efficiencies, marker='o', linestyle='-', color='green', label='Efficiency (Speedup / Threads)')
    plt.xlabel('Number of OpenMP Threads')
    plt.ylabel('Efficiency')
    plt.title('Efficiency vs. Number of Threads')
    plt.legend()
    plt.grid(True)
    plt.show()

# Executando a função
collect_results_and_plot('logs')
