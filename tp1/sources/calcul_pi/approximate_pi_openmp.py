#!/usr/bin/env python3
import matplotlib.pyplot as plt

def main():
    # Measured execution times (in seconds) for 1e9 samples
    execution_times = {
        1: 17.413845397,   # 1 thread
        2: 8.638714303,    # 2 threads
        4: 4.735207655,    # 4 threads
        8: 2.933302587,    # 8 threads
        16: 3.063921873,   # 16 threads
        32: 2.893393127,   # 32 threads
    }

    threads = sorted(execution_times.keys())
    times = [execution_times[t] for t in threads]
    baseline_time = execution_times[1]

    speedups = [baseline_time / execution_times[t] for t in threads]
    efficiencies = [(baseline_time / execution_times[t]) / t * 100 for t in threads]

    fig, (ax_speedup, ax_efficiency) = plt.subplots(2, 1, figsize=(8, 10), sharex=True)

    ax_speedup.plot(threads, speedups, marker='o', linestyle='-', color='b', label='Measured Speedup')
    ax_speedup.plot(threads, threads, marker='o', linestyle='--', color='r', label='Ideal Speedup')
    ax_speedup.set_title('Speedup vs. Number of Threads')
    ax_speedup.set_ylabel('Speedup (T(1)/T(n))')
    ax_speedup.legend()
    ax_speedup.grid(True)

    ax_efficiency.plot(threads, efficiencies, marker='s', linestyle='-', color='g', label='Efficiency')
    ax_efficiency.set_title('Efficiency vs. Number of Threads')
    ax_efficiency.set_xlabel('Number of Threads')
    ax_efficiency.set_ylabel('Efficiency (%)')
    ax_efficiency.legend()
    ax_efficiency.grid(True)

    plt.tight_layout()
    plt.savefig('plot.png')
    print("Plot saved as 'plot.png'")

if __name__ == '__main__':
    main()
