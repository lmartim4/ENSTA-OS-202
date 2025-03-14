import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import re
import os
import glob
from collections import defaultdict

def extract_metadata_and_data(filename):
    metadata = {}
    data_lines = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Capture "Taille du terrain : X"
            if line.startswith("Taille du terrain :"):
                match = re.search(r"Taille du terrain\s*:\s*(\d+)", line)
                if match:
                    metadata['terrain_size'] = int(match.group(1))
            
            # Capture "Nombre de cellules par direction : X"
            elif line.startswith("Nombre de cellules par direction :"):
                match = re.search(r"Nombre de cellules par direction\s*:\s*(\d+)", line)
                if match:
                    metadata['cells'] = int(match.group(1))
            
            # Capture "Vecteur vitesse : [x, y]"
            elif line.startswith("Vecteur vitesse :"):
                match = re.search(r"Vecteur vitesse\s*:\s*\[(\d+),\s*(\d+)\]", line)
                if match:
                    vx, vy = match.groups()
                    metadata['velocity'] = (int(vx), int(vy))
            
            # Capture "Position initiale du foyer (col, ligne) : col, line"
            elif line.startswith("Position initiale du foyer (col, ligne) :"):
                match = re.search(r"Position initiale du foyer \(col,\s*ligne\)\s*:\s*(\d+),\s*(\d+)", line)
                if match:
                    col, row = match.groups()
                    metadata['fire_col'] = int(col)
                    metadata['fire_row'] = int(row)
            
            # Capture "OpenMP threads: X"
            elif line.startswith("OpenMP threads:"):
                metadata['OpenMP_threads'] = int(line.split(":")[1].strip())
            
            # Capture data lines in the form "step,update_time,display_time,total_time"
            elif re.match(r'^\d+,\d+,\d+,\d+$', line):
                data_lines.append(line)
    
    # Convert data lines into a pandas DataFrame
    if data_lines:
        df = pd.DataFrame(
            [x.split(',') for x in data_lines], 
            columns=['step', 'update_time', 'display_time', 'total_time']
        ).astype({'step': int, 'update_time': int, 'display_time': int, 'total_time': int})
    else:
        raise ValueError("No valid data found in the file.")
    
    return metadata, df

def process_csv_files_by_thread_count(csv_files):
    # Dictionary to store DataFrames grouped by thread count
    thread_groups = defaultdict(list)
    
    # Process each CSV file
    for csv_file in csv_files:
        try:
            metadata, df = extract_metadata_and_data(csv_file)
            thread_count = metadata.get('OpenMP_threads', 'Unknown')
            
            # Store the DataFrame along with its metadata
            thread_groups[thread_count].append((metadata, df))
            print(f"Processed {csv_file} - Thread count: {thread_count}")
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    return thread_groups

def calculate_averages(thread_groups):
    average_results = {}
    
    for thread_count, file_data in thread_groups.items():
        if thread_count == 'Unknown':
            continue
            
        # Check if we have any data for this thread count
        if not file_data:
            continue
        
        # All dataframes for this thread count
        all_dfs = [data[1] for data in file_data]
        
        # Get a sample metadata (using the first file's metadata)
        sample_metadata = file_data[0][0]
        
        # For proper averaging, we need to align the step values
        # Find the maximum step value that appears in all dataframes
        min_max_step = min(df['step'].max() for df in all_dfs)
        
        # Filter dataframes to include only steps up to min_max_step
        filtered_dfs = [df[df['step'] <= min_max_step] for df in all_dfs]
        
        # Create a new DataFrame to store the average values
        avg_df = pd.DataFrame()
        avg_df['step'] = filtered_dfs[0]['step']  # Use steps from the first DataFrame
        
        # Calculate averages for each column
        avg_df['update_time'] = pd.concat([df['update_time'] for df in filtered_dfs], axis=1).mean(axis=1)
        avg_df['display_time'] = pd.concat([df['display_time'] for df in filtered_dfs], axis=1).mean(axis=1)
        avg_df['total_time'] = pd.concat([df['total_time'] for df in filtered_dfs], axis=1).mean(axis=1)
        
        # Store the average DataFrame and the sample metadata
        average_results[thread_count] = (sample_metadata, avg_df, len(file_data))
    
    return average_results

def plot_average_results(average_results, output_folder='plots'):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Create a combined plot for all thread counts
    plt.figure(figsize=(12, 8))
    
    # Colors for different thread counts
    colors = plt.cm.viridis(np.linspace(0, 1, len(average_results)))
    
    for i, (thread_count, (metadata, avg_df, file_count)) in enumerate(average_results.items()):
        # Extract other metadata for the legend
        cells = metadata.get('cells', 'Unknown')
        
        # Plot the average total time for this thread count
        plt.plot(
            avg_df['step'], 
            avg_df['total_time'] / 1000, 
            label=f'{thread_count} Threads (n={file_count})', 
            color=colors[i],
            linewidth=2
        )
    
    plt.xlabel('Step')
    plt.ylabel('Average Total Time (ms)')
    plt.title('Average Total Time by Thread Count')
    plt.legend()
    plt.grid(True)
    
    # Save the combined plot
    plt.savefig(os.path.join(output_folder, 'combined_thread_comparison.png'))
    plt.close()
    
    # Create individual plots for each thread count
    for thread_count, (metadata, avg_df, file_count) in average_results.items():
        # Extract relevant metadata
        cells = metadata.get('cells', 'Unknown')
        fire_col = metadata.get('fire_col', 'Unknown')
        fire_row = metadata.get('fire_row', 'Unknown')
        velocity = metadata.get('velocity', ('Unknown', 'Unknown'))
        
        # Create a descriptive title
        title_str = (
            f"Average Times - {thread_count} Threads (n={file_count})\n"
            f"n:{cells} - s({fire_col},{fire_row}) - w{velocity}"
        )
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(avg_df['step'], avg_df['update_time'] / 1000, label='Avg Update Time (ms)', color='green')
        plt.plot(avg_df['step'], avg_df['display_time'] / 1000, label='Avg Display Time (ms)', color='blue')
        plt.plot(avg_df['step'], avg_df['total_time'] / 1000, label='Avg Total Time (ms)', color='red')
        
        plt.xlabel('Step')
        plt.ylabel('Time (ms)')
        plt.title(title_str)
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        output_filename = os.path.join(output_folder, f'avg_thread_{thread_count}.png')
        plt.savefig(output_filename)
        plt.close()
        print(f"Plot saved as {output_filename}")

def main():
    # Specify the logs folder
    logs_folder = 'logs'
    
    # Find all CSV files in the logs folder
    csv_files = glob.glob(os.path.join(logs_folder, '*.csv'))
    
    if not csv_files:
        print("No CSV files found in the logs folder.")
        return
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Group files by thread count
    thread_groups = process_csv_files_by_thread_count(csv_files)
    
    # Calculate average results for each thread count
    average_results = calculate_averages(thread_groups)
    
    # Plot the average results
    plot_average_results(average_results)
    
    print("All processing completed.")

if __name__ == "__main__":
    main()