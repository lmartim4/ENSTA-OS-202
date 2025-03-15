#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

###############################################################################
# Helper Functions
###############################################################################

def read_csv_section(filepath):
    """
    Reads lines from `filepath` until finding the header
    'step,update_time,display_time,total_time'. After that, uses
    pandas.read_csv() to parse the data.

    Returns a DataFrame with columns [step, update_time, display_time, total_time]
    or an empty DF if the header was not found.
    """
    if not os.path.isfile(filepath):
        return pd.DataFrame(columns=["step", "update_time", "display_time", "total_time"])

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("step,update_time,display_time,total_time"):
            header_idx = i
            break

    if header_idx is None:
        return pd.DataFrame(columns=["step", "update_time", "display_time", "total_time"])

    data_str = "".join(lines[header_idx:])
    df = pd.read_csv(StringIO(data_str))
    return df


def average_rank_logs(logs_folder):
    """
    Inside `logs_folder`, we look for:
      - rank0*.csv => display_time
      - rank1*.csv => update_time
    We average them by step and compute total_time = update + display.

    Returns a DataFrame with columns:
      [step, update_time, display_time, total_time]
    or empty if data is missing.
    """
    if not os.path.isdir(logs_folder):
        return pd.DataFrame()

    rank0_files = glob.glob(os.path.join(logs_folder, "rank0*.csv"))
    rank1_files = glob.glob(os.path.join(logs_folder, "rank1*.csv"))
    if not rank0_files or not rank1_files:
        return pd.DataFrame()  # missing logs

    # Collect rank0 => display_time
    r0_dfs = []
    for f0 in rank0_files:
        df0 = read_csv_section(f0)
        if not df0.empty:
            r0_dfs.append(df0[["step", "display_time"]])

    # Collect rank1 => update_time
    r1_dfs = []
    for f1 in rank1_files:
        df1 = read_csv_section(f1)
        if not df1.empty:
            r1_dfs.append(df1[["step", "update_time"]])

    if not r0_dfs or not r1_dfs:
        return pd.DataFrame()

    df_r0_all = pd.concat(r0_dfs, ignore_index=True)
    df_r1_all = pd.concat(r1_dfs, ignore_index=True)

    # Average times by step
    df_r0_avg = df_r0_all.groupby("step", as_index=False)["display_time"].mean()
    df_r1_avg = df_r1_all.groupby("step", as_index=False)["update_time"].mean()

    df_merged = pd.merge(df_r0_avg, df_r1_avg, on="step", how="inner")
    df_merged["total_time"] = df_merged["display_time"] + df_merged["update_time"]
    return df_merged


def parse_omp_folder_name(folder_name):
    """
    Expects a folder name like 'benchmark_50_omp4':
      => N=50, T=4
    If we can't parse, returns (None, None).
    """
    # Find N
    N_match = re.search(r'benchmark_(\d+)_omp', folder_name)
    if not N_match:
        return None, None
    N_val = int(N_match.group(1))

    # Find T
    T_match = re.search(r'omp(\d+)', folder_name)
    if not T_match:
        return N_val, None

    T_val = int(T_match.group(1))
    return N_val, T_val

###############################################################################
# Main Logic
###############################################################################

def main():
    """
    1) Scan the current Etape_3 folder for directories named 'benchmark_<N>_omp<T>'.
    2) For each, read logs from the 'logs/' subfolder, average times, and store them in a dict:
         data_dict[(N, T)] = DataFrame of per-step times.
    3) Identify T=1 as baseline for each N, compute speedups for T>1:
         speedup = (time at T=1) / (time at T)
    4) Plot one figure per N, showing lines for update, display, and total speedup vs. T.
    5) Produce a global figure with total speedup for all N vs. T on one plot.
    6) Save a CSV summary of all speedups.
    
    We add a prefix 'mpi_vs_mpi_plus_omp_' to all image filenames.
    """
    script_dir = os.path.abspath(os.path.dirname(__file__))

    # 1) Gather subfolders named 'benchmark_<N>_omp<T>'
    subfolders = [
        d for d in os.listdir(script_dir)
        if d.startswith("benchmark_") and os.path.isdir(os.path.join(script_dir, d))
    ]

    # 2) Build data_dict with keys = (N, T)
    data_dict = {}

    for folder_name in subfolders:
        N_val, T_val = parse_omp_folder_name(folder_name)
        if (N_val is not None) and (T_val is not None):
            logs_folder = os.path.join(script_dir, folder_name, "logs")
            df_times = average_rank_logs(logs_folder)
            if not df_times.empty:
                data_dict[(N_val, T_val)] = df_times

    if not data_dict:
        print("[INFO] Aucun dossier 'benchmark_<N>_omp<T>/logs' contenant rank0/rank1 CSV n'a été trouvé.")
        return

    # 3) For each N, use T=1 as baseline. We'll compute speedup = baseline_time / T_time.
    from collections import defaultdict
    combos_by_N = defaultdict(list)
    for (N_val, T_val) in data_dict:
        combos_by_N[N_val].append(T_val)

    results = []
    for N_val, thread_list in combos_by_N.items():
        if 1 not in thread_list:
            # No T=1 => can't do speedup comparisons for this N
            continue
        df_baseline = data_dict[(N_val, 1)]

        for T_val in sorted(thread_list):
            df_current = data_dict[(N_val, T_val)]
            df_compare = pd.merge(
                df_baseline,
                df_current,
                on="step",
                suffixes=("_baseline", "_current"),
                how="inner"
            )
            if df_compare.empty:
                continue

            df_compare["update_speedup"] = (
                df_compare["update_time_baseline"] / df_compare["update_time_current"]
            )
            df_compare["display_speedup"] = (
                df_compare["display_time_baseline"] / df_compare["display_time_current"]
            )
            df_compare["total_speedup"] = (
                df_compare["total_time_baseline"] / df_compare["total_time_current"]
            )

            avg_up   = df_compare["update_speedup"].mean()
            avg_disp = df_compare["display_speedup"].mean()
            avg_tot  = df_compare["total_speedup"].mean()

            results.append({
                "N": N_val,
                "threads": T_val,
                "avg_update_speedup":  avg_up,
                "avg_display_speedup": avg_disp,
                "avg_total_speedup":   avg_tot
            })

    # 4) Make a DataFrame
    df_speedups = pd.DataFrame(results)
    if df_speedups.empty:
        print("[INFO] Impossible de calculer des speedups (aucun T=1 trouvé).")
        return

    df_speedups.sort_values(["N", "threads"], inplace=True)

    # 5) Plot one figure per N
    unique_Ns = df_speedups["N"].unique()
    for N_val in unique_Ns:
        df_sub = df_speedups[df_speedups["N"] == N_val]
        x      = df_sub["threads"]
        y_upd  = df_sub["avg_update_speedup"]
        y_disp = df_sub["avg_display_speedup"]
        y_tot  = df_sub["avg_total_speedup"]

        plt.figure()
        plt.plot(x, y_upd,  marker='o', label="Accélération mise à jour")
        plt.plot(x, y_disp, marker='o', label="Accélération affichage")
        plt.plot(x, y_tot,  marker='o', label="Accélération totale")

        plt.axhline(y=1, color='black', linestyle='--', label="Speedup = 1")
        plt.xlabel("Nombre de threads (T)")
        plt.ylabel("Speedup (T=1 / T)")
        plt.title(f"Speedups pour N={N_val}")
        plt.legend()
        plt.tight_layout()

        out_name = f"mpi_vs_mpi_plus_omp_speedups_N{N_val}.png"
        plt.savefig(out_name, dpi=150)
        plt.close()
        print(f"[OK] Graphique généré: {out_name}")

    # 6) Produce a global plot for total speedup vs. T, with lines for each N
    pivoted = df_speedups.pivot(index="threads", columns="N", values="avg_total_speedup")
    pivoted.sort_index(inplace=True)

    plt.figure()
    for col in pivoted.columns:
        plt.plot(pivoted.index, pivoted[col], marker='o', label=f"N={col}")
    plt.axhline(y=1, color='black', linestyle='--', label="Speedup = 1")

    plt.xlabel("Nombre de threads (T)")
    plt.ylabel("Speedup total (T=1 / T)")
    plt.title("Speedup global vs. nombre de threads (tous les N)")
    plt.legend()
    plt.tight_layout()

    outname_overall = "mpi_vs_mpi_plus_omp_speedups_overall_by_threads.png"
    plt.savefig(outname_overall, dpi=150)
    plt.close()
    print(f"[OK] Graphique global généré: {outname_overall}")

    # 7) Save CSV summary
    out_csv = "mpi_vs_mpi_plus_omp_omp_speedups_summary.csv"
    df_speedups.to_csv(out_csv, index=False)
    print(f"[OK] Résumé des speedups sauvegardé dans: {out_csv}")


if __name__ == "__main__":
    main()
