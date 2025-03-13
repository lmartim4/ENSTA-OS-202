#!/bin/bash

# Definir diretórios
BUILD_DIR="build"
LOG_DIR="logs"

# Remover todos os arquivos do diretório logs
if [ -d "$LOG_DIR" ]; then
    echo "Limpando diretório de logs..."
    rm -rf "$LOG_DIR"/*
else
    echo "Diretório de logs não encontrado. Pulando a limpeza."
fi

# Navegar para o diretório build
cd build || { echo "Build directory not found!"; exit 1; }

# Compilar o projeto
echo "Compilando o projeto..."
cmake --build .

# Verificar se a compilação foi bem-sucedida
if [ ! -f "simulation.exe" ]; then
    echo "Erro: Compilation failed or simulation.exe not found!"
    exit 1
fi

# Criar um arquivo de saída para armazenar os tempos de execução
OUTPUT_FILE="../execution_times.txt"
echo "Threads,Time(s)" > "$OUTPUT_FILE"

# Executar a simulação variando OMP_NUM_THREADS
echo "Executando simulação com diferentes quantidades de threads..."
for threads in 1 2 12; do
    echo "Executando com OMP_NUM_THREADS=$threads"
    export OMP_NUM_THREADS=$threads
    
    ./simulation.exe -n 100
    echo "----------------------------------------"
done

# Voltar para o diretório raiz
cd ..

# Executar o script Python para plotar os resultados
echo "Gerando gráfico de Speedup..."
python3 speedup_plot.py

echo "Processo concluído!"
