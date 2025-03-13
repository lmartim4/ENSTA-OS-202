#!/usr/bin/env python3
import matplotlib.pyplot as plt

def main():
    # Data extracted from your output:
    threads = [1, 2, 4, 6, 8, 12, 16, 32, 64, 128, 256]
    cpu_times = [8.42875, 4.55329, 2.23407, 1.49052, 1.11897, 0.844645, 0.740617, 0.680056, 0.619166, 0.594932, 0.620733]
    mflops = [254.781, 471.634, 961.244, 1440.76, 1919.16, 2542.47, 2899.59, 3157.81, 3468.35, 3609.63, 3459.59]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left plot: CPU Time
    ax1.plot(threads, cpu_times, marker='o', linestyle='-', color='blue')
    ax1.set_xlabel("OMP_NUM_THREADS")
    ax1.set_ylabel("CPU Time (s)")
    ax1.set_title("CPU Time vs OMP_NUM_THREADS")
    ax1.set_xscale('log', base=2)
    ax1.set_xticks(threads)
    ax1.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax1.grid(True, which="both", ls="--", alpha=0.5)

    # Right plot: MFLOPS
    ax2.plot(threads, mflops, marker='s', linestyle='-', color='red')
    ax2.set_xlabel("OMP_NUM_THREADS")
    ax2.set_ylabel("MFLOPS")
    ax2.set_title("MFLOPS vs OMP_NUM_THREADS")
    ax2.set_xscale('log', base=2)
    ax2.set_xticks(threads)
    ax2.get_xaxis().set_major_formatter(plt.ScalarFormatter())
    ax2.grid(True, which="both", ls="--", alpha=0.5)

    plt.suptitle("Matrix Product Performance vs OMP_NUM_THREADS", y=0)
    plt.tight_layout()
    plt.show()
    plt.close()
    
if __name__ == "__main__":
    main()
