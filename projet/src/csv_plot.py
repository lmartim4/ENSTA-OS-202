import matplotlib.pyplot as plt
import pandas as pd
import sys
import re

def extract_metadata_and_data(filename):
    metadata = {}
    data_lines = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Try to capture OpenMP threads and other metadata
            if line.startswith("OpenMP threads:"):
                metadata['OpenMP threads'] = int(line.split(":")[1].strip())
            elif re.match(r'^\d+,\d+,\d+,\d+$', line):
                data_lines.append(line)
            
    # Convert data lines into a pandas DataFrame
    if data_lines:
        df = pd.DataFrame([x.split(',') for x in data_lines], 
                          columns=['step', 'update_time', 'display_time', 'total_time'])
        df = df.astype({'step': int, 'update_time': int, 'display_time': int, 'total_time': int})
    else:
        raise ValueError("No valid data found in the file.")
    
    return metadata, df

def plot_csv(filename):
    try:
        metadata, df = extract_metadata_and_data(filename)
    except Exception as e:
        print(f"Error: {e}")
        return
    
    omp_threads = metadata.get('OpenMP threads', 'Unknown')
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['step'], df['update_time'] / 1000, label='Update Time (ms)', color='green')
    plt.plot(df['step'], df['display_time'] / 1000, label='Display Time (ms)', color='blue')
    plt.plot(df['step'], df['total_time'] / 1000, label='Total Time (ms)', color='red')

    plt.xlabel('Step')
    plt.ylabel('Time (ms)')
    plt.title(f'Execution Timing Analysis (OpenMP threads: {omp_threads})')
    plt.legend()
    plt.grid(True)
    
    # Save the figure with the same filename but .png extension
    output_filename = filename.replace('.csv', '.png')
    plt.savefig(output_filename)
    print(f"Plot saved as {output_filename}")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_csv.py <filename.csv>")
    else:
        plot_csv(sys.argv[1])
