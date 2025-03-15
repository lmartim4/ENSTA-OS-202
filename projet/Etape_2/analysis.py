import os
import re
import glob
import pandas as pd
import matplotlib.pyplot as plt

def load_profiling_csv(filepath):
    """
    Lê um único arquivo CSV de log.
    Pula todas as linhas até encontrar o cabeçalho:
       step,update_time,display_time,total_time
    Retorna um DataFrame com as colunas:
       [ 'step', 'update_time', 'display_time', 'total_time' ]
    E converte de microsegundos (µs) para milissegundos (ms).
    """
    rows = []
    found_header = False
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Detecta a linha "step,update_time,display_time,total_time"
            if not found_header:
                if line.startswith("step,"):
                    found_header = True
                continue  # Pula linhas até encontrar o cabeçalho
            
            # A partir daqui, lê as linhas de dados:
            if line:
                parts = line.split(',')
                if len(parts) == 4:
                    try:
                        step = int(parts[0])
                        update = float(parts[1])
                        disp = float(parts[2])
                        total = float(parts[3])
                        rows.append((step, update, disp, total))
                    except ValueError:
                        # Caso algum valor não seja numérico, pula
                        pass

    df = pd.DataFrame(rows, columns=["step", "update_time", "display_time", "total_time"])
    
    # Ignora a primeira linha (se houver mais de 1)
    if len(df) > 1:
        df = df.iloc[1:].reset_index(drop=True)

    # Converte de microsegundos para milissegundos
    if not df.empty:
        df["update_time"] = df["update_time"] / 1000.0
        df["display_time"] = df["display_time"] / 1000.0
        df["total_time"] = df["total_time"] / 1000.0

    return df

def main():
    logs_folder = "logs"   # Pasta contendo os CSVs
    pattern = os.path.join(logs_folder, "rank*.csv")
    csv_files = glob.glob(pattern)

    if not csv_files:
        print(f"Nenhum arquivo encontrado em: {pattern}")
        return

    # Cria a pasta para as figuras, se não existir
    figures_folder = os.path.join(logs_folder, "figures")
    os.makedirs(figures_folder, exist_ok=True)

    # Dicionário: rank -> list of DataFrames
    data_by_rank = {}

    # Extrai o número do rank dos nomes de arquivos do tipo "rank<rank>.csv"
    rank_pattern = re.compile(r"rank(\d+)")

    for filepath in csv_files:
        filename = os.path.basename(filepath)
        match = rank_pattern.search(filename)
        if not match:
            continue
        rank = int(match.group(1))

        df = load_profiling_csv(filepath)
        if df.empty:
            continue

        if rank not in data_by_rank:
            data_by_rank[rank] = []
        data_by_rank[rank].append(df)

    # Para cada rank, combina todos os DataFrames, agrupa por step e calcula a média
    for rank, df_list in data_by_rank.items():
        combined_df = pd.concat(df_list, ignore_index=True)
        # Agrupa por step e calcula a média de cada coluna
        avg_df = combined_df.groupby("step").mean().reset_index()

        # 1) Gráfico do update_time (em ms)
        plt.figure()
        plt.title(f"Rank {rank} - Update Time (Média em ms)")
        plt.xlabel("step")
        plt.ylabel("update_time (ms)")
        plt.plot(avg_df["step"], avg_df["update_time"], marker="o")
        plt.savefig(os.path.join(figures_folder, f"rank_{rank}_update_time.png"))
        plt.close()

        # 2) Gráfico do display_time (em ms)
        plt.figure()
        plt.title(f"Rank {rank} - Display Time (Média em ms)")
        plt.xlabel("step")
        plt.ylabel("display_time (ms)")
        plt.plot(avg_df["step"], avg_df["display_time"], marker="o")
        plt.savefig(os.path.join(figures_folder, f"rank_{rank}_display_time.png"))
        plt.close()

        # 3) Gráfico do total_time (em ms)
        plt.figure()
        plt.title(f"Rank {rank} - Total Time (Média em ms)")
        plt.xlabel("step")
        plt.ylabel("total_time (ms)")
        plt.plot(avg_df["step"], avg_df["total_time"], marker="o")
        plt.savefig(os.path.join(figures_folder, f"rank_{rank}_total_time.png"))
        plt.close()

        print(f"[OK] Gráficos gerados para rank {rank}")

        global_avg_total_time = avg_df["total_time"].mean()
        print(f"Rank {rank}: Global mean total_time = {global_avg_total_time} ms")

if __name__ == "__main__":
    main()
