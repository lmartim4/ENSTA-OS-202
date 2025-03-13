#!/bin/bash

BUILD_DIR="build"
LOG_DIR="logs"

if [ -d "$LOG_DIR" ]; then
    echo "Cleaning old logs..."
    rm -rf "$LOG_DIR"/*
else
    echo "Diretório de logs não encontrado. Pulando a limpeza."
fi

cd build || { echo "Build directory not found!"; exit 1; }

echo "Compilando o projeto..."
cmake --build .

if [ ! -f "simulation.exe" ]; then
    echo "Erro: Compilation failed or simulation.exe not found!"
    exit 1
fi

for threads in 1 2 3 4 5 6 7 8 9 10 11 12; do
    echo "Executando com OMP_NUM_THREADS=$threads"
    export OMP_NUM_THREADS=$threads
    ./simulation.exe -n 300
    echo "----------------------------------------"
done

cd ..

echo "Gerando gráfico de Speedup..."
python speedup_plot.py

echo "Processo concluído!"
