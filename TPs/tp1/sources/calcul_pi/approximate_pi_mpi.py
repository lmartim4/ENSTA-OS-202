#!/usr/bin/env python3
import matplotlib.pyplot as plt

def main():
    # Data from your experiments:
    # Number of MPI processes used
    processes = [1, 2, 4, 8]
    # Execution times in seconds (obtained from your runs)
    times = [18.7999, 12.6982, 5.07721, 3.39508]

    # Compute speedup relative to the single-process execution time.
    # Speedup S(p) = T(1) / T(p)
    base_time = times[0]
    speedup = [base_time / t for t in times]

    # Create a figure with two subplots: one for execution times, one for speedup
    plt.figure(figsize=(12, 5))

    # --- Plot 1: Execution Time vs. Number of Processes ---
    plt.subplot(1, 2, 1)
    plt.plot(processes, times, marker='o', linestyle='-', color='blue')
    plt.xlabel("Number of Processes")
    plt.ylabel("Execution Time (s)")
    plt.title("Execution Time vs. Number of Processes")
    plt.xticks(processes)
    plt.grid(True)

    # --- Plot 2: Speedup vs. Number of Processes ---
    plt.subplot(1, 2, 2)
    plt.plot(processes, speedup, marker='o', linestyle='-', color='green')
    plt.xlabel("Number of Processes")
    plt.ylabel("Speedup")
    plt.title("Speedup vs. Number of Processes")
    plt.xticks(processes)
    plt.grid(True)

    # Adjust layout to prevent overlapping labels and show the plots
    plt.tight_layout()
    plt.savefig("pi_MPI.png")

if __name__ == "__main__":
    main()
