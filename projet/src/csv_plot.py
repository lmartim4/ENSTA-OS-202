import matplotlib.pyplot as plt
import pandas as pd
import sys

def plot_csv(filename):
    # Read the CSV file
    with open(filename, 'r') as file:
        first_line = file.readline().strip()
    
    # Extract OpenMP threads count
    try:
        omp_threads = int(first_line.split(":")[1].strip())
    except (IndexError, ValueError):
        print("Error: Could not extract OpenMP thread count from the file.")
        return
    
    # Read the actual data, skipping the first line
    df = pd.read_csv(filename, skiprows=1)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['step'], df['update_time']/1000, label='Update Time (ms)', color='green')
    plt.plot(df['step'], df['display_time']/1000, label='Display Time (ms)', color='blue')
    plt.plot(df['step'], df['total_time']/1000, label='Total Time (ms)',color='red')

    plt.xlabel('Step')
    plt.ylabel('Time (ms)')
    plt.title(f'Execution Timing Analysis (OpenMP threads: {omp_threads})')
    plt.legend()
    plt.grid(True)  # Make grid lines thinner

    # Save the figure with the same filename but .png extension
    output_filename = filename.replace('.csv', '.png')
    plt.savefig(output_filename)
    print(f"Plot saved as {output_filename}")

# Example msage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("msage: python plot_csv.py <filename.csv>")
    else:
        plot_csv(sys.argv[1])
