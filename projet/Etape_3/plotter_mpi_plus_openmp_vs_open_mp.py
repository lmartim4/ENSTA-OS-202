#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

###############################################################################
# Helper functions
###############################################################################

def read_csv_section(filepath):
    """
    Reads lines from `filepath` until finding the header
    'step,update_time,display_time,total_time'. After that, uses
    pandas.read_csv() to parse the data.

    Returns a DataFrame with columns:
        step, update_time, display_time, total_time
    or an empty DF if the header was not found.
    """
    if not os.path.isfile(filepath):
        return pd.DataFrame(columns=["step", "update_time", "display_time", "total_time"])

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("step,update_time,display_time,total_time"):
            header_index = i
            break

    if header_index is None:
        # Header not found
        return pd.DataFrame(columns=["step", "update_time", "display_time", "total_time"])

    data_str = "".join(lines[header_index:])
    df = pd.read_csv(StringIO(data_str))
    return df


def average_non_mpi_logs(folder_with_logs):
    """
    Reads all .csv files in 'folder_with_logs' (non-MPI logs).
    Aggregates them by averaging update_time, display_time, and total_time 
    (grouped by step).

    Returns a DataFrame with columns:
        step, update_time, display_time, total_time  (averaged)
    or an empty DataFrame if not found.
    """
    if not os.path.isdir(folder_with_logs):
        return pd.DataFrame()

    csv_files = glob.glob(os.path.join(folder_with_logs, "*.csv"))
    dfs = []
    for f in csv_files:
        df = read_csv_section(f)
        if not df.empty:
            dfs.append(df)
    if not dfs:
        return pd.DataFrame()

    df_all = pd.concat(dfs, ignore_index=True)
    df_avg = (
        df_all
        .groupby("step", as_index=False)[["update_time", "display_time", "total_time"]]
        .mean()
    )
    return df_avg


def average_omp_logs(folder_with_logs):
    """
    Reads rank0*.csv (display times) and rank1*.csv (update times) from 'folder_with_logs'
    for the MPI+OpenMP run.

    We average them separately and merge into a single DF with columns:
        step, update_time, display_time, total_time

    or an empty DataFrame if not found / incomplete.
    """
    if not os.path.isdir(folder_with_logs):
        return pd.DataFrame()

    # rank0 => display_time
    rank0_files = glob.glob(os.path.join(folder_with_logs, "rank0*.csv"))
    r0_dfs = []
    for f0 in rank0_files:
        df_r0 = read_csv_section(f0)
        if not df_r0.empty:
            # keep only step and display_time
            r0_dfs.append(df_r0[["step","display_time"]])

    # rank1 => update_time
    rank1_files = glob.glob(os.path.join(folder_with_logs, "rank1*.csv"))
    r1_dfs = []
    for f1 in rank1_files:
        df_r1 = read_csv_section(f1)
        if not df_r1.empty:
            # keep only step and update_time
            r1_dfs.append(df_r1[["step","update_time"]])

    if not r0_dfs or not r1_dfs:
        # If we can't find logs for rank0 or rank1, no data.
        return pd.DataFrame()

    df_r0_all = pd.concat(r0_dfs, ignore_index=True)
    df_r0_avg = df_r0_all.groupby("step", as_index=False)["display_time"].mean()

    df_r1_all = pd.concat(r1_dfs, ignore_index=True)
    df_r1_avg = df_r1_all.groupby("step", as_index=False)["update_time"].mean()

    # Merge and define total_time
    df_mpi_avg = pd.merge(df_r0_avg, df_r1_avg, on="step", how="inner")
    df_mpi_avg["total_time"] = df_mpi_avg["update_time"] + df_mpi_avg["display_time"]
    return df_mpi_avg


def extract_N_from_name(folder_name):
    """
    Extract integer <N> from names like 'benchmark_100' or 'benchmark_100_omp4'.
    Returns None if not found.
    """
    m = re.search(r'benchmark_(\d+)', folder_name)
    if m:
        return int(m.group(1))
    return None

def extract_threads_from_name(folder_name):
    """
    Extract integer T from names like 'benchmark_100_omp4' => T=4.
    Returns None if not found (which could indicate a non-OMP folder).
    """
    m = re.search(r'omp(\d+)', folder_name)
    if m:
        return int(m.group(1))
    return None

###############################################################################
# Main script logic
###############################################################################

def main():
    # We consider we're in "Etape_3" folder.
    # 1) Non-MPI data is in ../Etape_1/benchmarks/benchmark_<N>/logs
    # 2) Hybrid (OMP) data is in ./benchmark_<N>_omp<T>/logs

    # Adjust these base paths to your actual structure if needed.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # If you want absolute paths, replace with e.g.:
    # non_mpi_base_path = "/home/lmartim4/ENSTA-OS-202/projet/Etape_1/benchmarks"
    # omp_base_path     = "/home/lmartim4/ENSTA-OS-202/projet/Etape_3"
    non_mpi_base_path = os.path.join(script_dir, "..", "Etape_1", "benchmarks")
    omp_base_path     = script_dir  # current directory for OMP logs

    # We'll store each baseline in a dict { N: DataFrame_of_averaged_times }
    baseline_dict = {}

    # 1) Gather baseline (non-MPI) logs from ../Etape_1/benchmarks/benchmark_<N>/logs
    #    e.g.: .../benchmark_50/logs/*.csv
    for folder_name in os.listdir(non_mpi_base_path):
        if folder_name.startswith("benchmark_"):
            N_val = extract_N_from_name(folder_name)
            if N_val is None:
                continue  # skip if we can't parse N

            # Inside this folder, there's a "logs" subfolder
            logs_path = os.path.join(non_mpi_base_path, folder_name, "logs")
            df_base = average_non_mpi_logs(logs_path)
            if not df_base.empty:
                baseline_dict[N_val] = df_base

    # 2) For the hybrid logs, we parse the local "Etape_3" folder for "benchmark_<N>_omp<T>"
    results = []
    for folder_name in os.listdir(omp_base_path):
        if folder_name.startswith("benchmark_"):
            N_val = extract_N_from_name(folder_name)
            T_val = extract_threads_from_name(folder_name)
            if N_val is not None and T_val is not None:
                # We'll look for logs in <folder>/logs
                logs_path = os.path.join(omp_base_path, folder_name, "logs")
                df_omp = average_omp_logs(logs_path)
                if not df_omp.empty and (N_val in baseline_dict):
                    # Compare with baseline for the same N
                    df_base = baseline_dict[N_val]

                    # Merge on step
                    df_compare = pd.merge(
                        df_base,
                        df_omp,
                        on="step",
                        suffixes=("_base", "_omp"),
                        how="inner"
                    )
                    if not df_compare.empty:
                        # speedup = base_time / omp_time
                        df_compare["update_speedup"] = (
                            df_compare["update_time_base"] / df_compare["update_time_omp"]
                        )
                        df_compare["display_speedup"] = (
                            df_compare["display_time_base"] / df_compare["display_time_omp"]
                        )
                        df_compare["total_speedup"] = (
                            df_compare["total_time_base"] / df_compare["total_time_omp"]
                        )

                        avg_update_speedup  = df_compare["update_speedup"].mean()
                        avg_display_speedup = df_compare["display_speedup"].mean()
                        avg_total_speedup   = df_compare["total_speedup"].mean()

                        results.append({
                            "N": N_val,
                            "threads": T_val,
                            "avg_update_speedup":  avg_update_speedup,
                            "avg_display_speedup": avg_display_speedup,
                            "avg_total_speedup":   avg_total_speedup
                        })

    # 3) Create a DataFrame of results
    df_speedups = pd.DataFrame(results)
    if df_speedups.empty:
        print("No valid data found (either no baseline or no OMP logs). Exiting.")
        return

    # 4) Sort by N then threads
    df_speedups.sort_values(["N","threads"], inplace=True)

    # 5) Plot speedups vs. threads for each distinct N (separate plots)
    unique_Ns = sorted(df_speedups["N"].unique())
    for N_val in unique_Ns:
        df_sub = df_speedups[df_speedups["N"] == N_val]
        x_threads   = df_sub["threads"]
        y_update    = df_sub["avg_update_speedup"]
        y_display   = df_sub["avg_display_speedup"]
        y_total     = df_sub["avg_total_speedup"]

        plt.figure()
        plt.plot(x_threads, y_update,  marker='o', label="Speedup (update)")
        plt.plot(x_threads, y_display, marker='o', label="Speedup (display)")
        plt.plot(x_threads, y_total,   marker='o', label="Speedup (total)")

        # Horizontal line at speedup = 1
        plt.axhline(y=1, color='black', linestyle='--', label="Speedup = 1")

        plt.xlabel("Nombre de threads (T)")
        plt.ylabel("Accélération (temps_seq / temps_omp)")
        plt.title(f"Accélérations MPI+OpenMP pour N={N_val}")
        plt.legend()
        plt.tight_layout()

        outname = f"speedups_N{N_val}.png"
        plt.savefig(outname, dpi=150)
        plt.close()
        print(f"[OK] Graphique généré : {outname}")

    # 6) (NEW) Create a final plot to see the overall total speedup vs. thread count,
    #           with one line per distinct N. This helps visualize the "general" scaling
    #           behavior with T.
    pivoted = df_speedups.pivot(index="threads", columns="N", values="avg_total_speedup")
    pivoted.sort_index(inplace=True)

    plt.figure()
    for col in pivoted.columns:
        plt.plot(pivoted.index, pivoted[col], marker='o', label=f"N={col}")

    plt.axhline(y=1, color='black', linestyle='--', label="Speedup = 1")
    plt.xlabel("Nombre de threads (T)")
    plt.ylabel("Accélération totale (temps_seq / temps_omp)")
    plt.title("Accélération totale vs. nombre de threads (tous les N)")
    plt.legend()
    plt.tight_layout()

    outname_global = "speedups_overall_by_threads.png"
    plt.savefig(outname_global, dpi=150)
    plt.close()
    print(f"[OK] Graphique global généré : {outname_global}")

    # 7) Save a CSV summary
    out_csv = "omp_mpi_speedups_summary.csv"
    df_speedups.reset_index(drop=True, inplace=True)
    df_speedups.to_csv(out_csv, index=False)
    print(f"[OK] Résumé des speedups sauvegardé dans {out_csv}.")


if __name__ == "__main__":
    main()
