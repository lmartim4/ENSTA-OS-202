import matplotlib.pyplot as plt
import pandas as pd
import sys
import re
import os
import glob

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
                metadata['OpenMP threads'] = int(line.split(":")[1].strip())
            
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

def plot_csv(filename):
    try:
        metadata, df = extract_metadata_and_data(filename)
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return
    
    # Extract relevant metadata (using .get(...) with fallback "Unknown")
    omp_threads = metadata.get('OpenMP threads', 'Unknown')
    cells = metadata.get('cells', 'Unknown')
    fire_col = metadata.get('fire_col', 'Unknown')
    fire_row = metadata.get('fire_row', 'Unknown')
    velocity = metadata.get('velocity', ('Unknown', 'Unknown'))
    
    # Create a descriptive title using the extracted metadata
    title_str = (
        f"- n:{cells} "
        f"- s({fire_col},{fire_row}) "
        f"- w{velocity} "
        f"- OpenMP threads: {omp_threads}"
    )
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['step'], df['update_time'] / 1000, label='Update Time (ms)', color='green')
    plt.plot(df['step'], df['display_time'] / 1000, label='Display Time (ms)', color='blue')
    plt.plot(df['step'], df['total_time'] / 1000, label='Total Time (ms)', color='red')

    plt.xlabel('Step')
    plt.ylabel('Time (ms)')
    plt.title(title_str)
    plt.legend()
    plt.grid(True)
    
    # Save the figure with the same filename but .png extension
    output_filename = filename.replace('.csv', '.png')
    plt.savefig(output_filename)
    plt.close()  # Close the figure to free up memory
    print(f"Plot saved as {output_filename}")

def main():
    # Specify the logs folder
    logs_folder = 'logs'
    
    # Find all CSV files in the logs folder
    csv_files = glob.glob(os.path.join(logs_folder, '*.csv'))
    
    if not csv_files:
        print("No CSV files found in the logs folder.")
        return
    
    # Process each CSV file
    for csv_file in csv_files:
        print(f"Processing {csv_file}...")
        plot_csv(csv_file)

if __name__ == "__main__":
    main()
