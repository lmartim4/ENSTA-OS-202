#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
benchmark_plotter.py
--------------------
Este script procura por todas as pastas que comecem com 'benchmarkAnalysis_'
no diretório atual, e em cada uma delas executa o mesmo processo que fazíamos
no speedup_plot.py:
  1) Identificar arquivos 'sequenciais' (sem 'rank' no nome) e arquivos rank0/rank1.
  2) Ler/mesclar/averiguar os tempos.
  3) Calcular speedup (seq_time / mpi_time).
  4) Gerar e salvar um gráfico de speedup (update, display, total) dentro da
     própria pasta ou no diretório atual.

Uso:
  $ python benchmark_plotter.py
  (Ou torne-o executável e rode ./benchmark_plotter.py)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

def read_csv_section(filepath):
    """
    Lê as linhas de `filepath` até encontrar o cabeçalho
    'step,update_time,display_time,total_time'. Depois disso,
    usa pandas.read_csv() para carregar (header + linhas subsequentes).

    Retorna um DataFrame com colunas:
        step, update_time, display_time, total_time
    ou um DF vazio se não encontrar o cabeçalho.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("step,update_time,display_time,total_time"):
            header_index = i
            break

    if header_index is None:
        print(f"[AVISO] Cabeçalho não encontrado no arquivo: {filepath}")
        return pd.DataFrame(columns=["step", "update_time", "display_time", "total_time"])

    data_str = "".join(lines[header_index:])
    df = pd.read_csv(StringIO(data_str))
    return df


def process_folder(dir_path):
    """
    Executa o processo de:
      1) Achar arquivos sequenciais (sem 'rank' no nome) e rank0/rank1
      2) Ler e concatenar DataFrames -> agrupar por 'step' e tirar média
      3) Calcular total_time_mpi = update_time_mpi + display_time_mpi
      4) Calcular speedup = seq / mpi
      5) Plotar e salvar grafico 'plot_<nome_da_pasta>.png'
    Retorna o DataFrame final de comparação ou vazio se algo falhar.
    """

    # Lista de arquivos
    all_files = os.listdir(dir_path)

    seq_files   = [f for f in all_files if "rank" not in f]            # sequenciais
    rank0_files = [f for f in all_files if f.startswith("rank0")]      # rank0
    rank1_files = [f for f in all_files if f.startswith("rank1")]      # rank1

    # Ler e agrupar SEQUENCIAIS
    seq_dfs = []
    for sf in seq_files:
        df_raw = read_csv_section(os.path.join(dir_path, sf))
        if not df_raw.empty:
            df_seq = df_raw[["step","update_time","display_time","total_time"]].copy()
            seq_dfs.append(df_seq)

    if len(seq_dfs) == 0:
        print(f"[INFO] Nenhum arquivo SEQUENCIAL encontrado em {dir_path}.")
        return pd.DataFrame()

    df_seq_all = pd.concat(seq_dfs, ignore_index=True)
    df_seq_avg = (
        df_seq_all
        .groupby("step", as_index=False)[["update_time","display_time","total_time"]]
        .mean()
    )
    df_seq_avg.rename(columns={
        "update_time":"update_time_seq",
        "display_time":"display_time_seq",
        "total_time":"total_time_seq"
    }, inplace=True)

    # rank0 => só display_time => display_time_mpi
    r0_dfs = []
    for f0 in rank0_files:
        df_raw = read_csv_section(os.path.join(dir_path, f0))
        if not df_raw.empty:
            df_r0 = df_raw[["step","display_time"]].copy()
            df_r0.rename(columns={"display_time":"display_time_mpi"}, inplace=True)
            r0_dfs.append(df_r0)

    if len(r0_dfs) == 0:
        print(f"[INFO] Nenhum arquivo rank0 encontrado em {dir_path}.")
        return pd.DataFrame()

    df_r0_all = pd.concat(r0_dfs, ignore_index=True)
    df_r0_avg = (
        df_r0_all
        .groupby("step", as_index=False)["display_time_mpi"]
        .mean()
    )

    # rank1 => só update_time => update_time_mpi
    r1_dfs = []
    for f1 in rank1_files:
        df_raw = read_csv_section(os.path.join(dir_path, f1))
        if not df_raw.empty:
            df_r1 = df_raw[["step","update_time"]].copy()
            df_r1.rename(columns={"update_time":"update_time_mpi"}, inplace=True)
            r1_dfs.append(df_r1)

    if len(r1_dfs) == 0:
        print(f"[INFO] Nenhum arquivo rank1 encontrado em {dir_path}.")
        return pd.DataFrame()

    df_r1_all = pd.concat(r1_dfs, ignore_index=True)
    df_r1_avg = (
        df_r1_all
        .groupby("step", as_index=False)["update_time_mpi"]
        .mean()
    )

    # Merge r0 & r1
    df_mpi_avg = pd.merge(df_r0_avg, df_r1_avg, on="step", how="inner")

    # Define total_time_mpi = update_time_mpi + display_time_mpi
    df_mpi_avg["total_time_mpi"] = df_mpi_avg["update_time_mpi"] + df_mpi_avg["display_time_mpi"]

    # Comparar seq vs MPI
    df_compare = pd.merge(
        df_seq_avg,
        df_mpi_avg[["step","update_time_mpi","display_time_mpi","total_time_mpi"]],
        on="step",
        how="inner"
    )
    if df_compare.empty:
        print(f"[INFO] Dados vazios após merge (seq e mpi) em {dir_path} => talvez steps não coincidam.")
        return df_compare

    # Calcular speedup = seq_time / mpi_time
    df_compare["update_speedup"]  = df_compare["update_time_seq"]   / df_compare["update_time_mpi"]
    df_compare["display_speedup"] = df_compare["display_time_seq"]  / df_compare["display_time_mpi"]
    df_compare["total_speedup"]   = df_compare["total_time_seq"]    / df_compare["total_time_mpi"]

    # Plotar
    plt.figure()
    plt.plot(df_compare["step"], df_compare["update_speedup"],  label="Update Speedup")
    plt.plot(df_compare["step"], df_compare["display_speedup"], label="Display Speedup")
    plt.plot(df_compare["step"], df_compare["total_speedup"],   label="Total Speedup")
    plt.xlabel("Step")
    plt.ylabel("Speedup (Seq / MPI)")
    plt.title(f"Speedups - {os.path.basename(dir_path)}")
    plt.legend()

    # Salva o plot no diretório atual (ou pode salvar dentro da pasta)
    outname = f"plot_{os.path.basename(dir_path)}.png"
    plt.savefig(outname, dpi=150)
    plt.close()

    print(f"[OK] Gerado gráfico: {outname}")

    # (Opcional) poderíamos salvar o CSV:
    # csv_out = f"speedup_data_{os.path.basename(dir_path)}.csv"
    # df_compare.to_csv(csv_out, index=False)

    return df_compare


def main():
    """
    Procura por todas as pastas que começam com 'benchmarkAnalysis_' no
    diretório atual, chama process_folder(pasta) para cada uma e gera
    os gráficos e merges.
    """
    cwd = os.getcwd()
    # Listar subdiretórios
    dirs = [d for d in os.listdir(cwd) 
            if d.startswith("benchmarkAnalysis_") and os.path.isdir(d)]

    if not dirs:
        print("Não há pastas iniciando com 'benchmarkAnalysis_' aqui.")
        return

    for d in dirs:
        print(f"\n>>> Processando pasta: {d}")
        df_result = process_folder(d)
        if df_result.empty:
            print(f"[AVISO] A pasta '{d}' não gerou dados válidos.\n")


if __name__ == "__main__":
    main()
