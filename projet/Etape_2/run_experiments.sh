#!/bin/bash
# Script para compilar o projeto na pasta build, executar a simulação múltiplas vezes
# para diferentes valores de N, rodar o analysis.py e renomear a pasta logs para logs_N.
#
# Ele:
#   1) Entra na pasta build, compila (cmake --build .)
#   2) Executa mpiexec -n 2 ./simulation.exe -n N várias vezes
#   3) Roda analysis.py
#   4) Renomeia logs para logs_N
#   5) Volta para a pasta anterior
#   6) Intercepta Ctrl+C para encerrar de forma limpa

# Número de execuções para cada valor de N
NUM_RUNS=5

# Função para tratar Ctrl+C (SIGINT)
cleanup() {
    echo "Recebido Ctrl+C. Encerrando o script..."
    exit 1
}

# Configura o trap para SIGINT (Ctrl+C)
trap cleanup SIGINT

# Entra na pasta build
echo "Entrando na pasta build..."
pushd build || { echo "Pasta build não encontrada."; exit 1; }

# Compila o projeto
echo "Compilando com cmake --build ."
cmake --build .

# (Opcional) Remove logs antigos dentro de build, se existir
if [ -d "logs" ]; then
    echo "Removendo logs antigos..."
    rm -rf logs
fi

# Lista de valores de N
for N in 50 100 200 400 800; do
    echo "--------------------------------------------------"
    echo "Executando simulação para N = ${N}"
    echo "--------------------------------------------------"

    # Remove a pasta logs se existir de execuções anteriores
    if [ -d "logs" ]; then
        rm -rf logs
    fi

    # Executa a simulação NUM_RUNS vezes para o valor de N
    for (( i=1; i<=NUM_RUNS; i++ )); do
        echo "Execução ${i} de ${NUM_RUNS} com -n ${N}"
        mpiexec -n 2 ./simulation.exe -n "${N}"
    done

    # Roda o script Python de análise
    echo "Executando analysis.py para N = ${N}"
    cd ..
    python analysis.py

    # Renomeia a pasta logs para logs_N
    if [ -d "logs" ]; then
        mv logs "logs_${N}"
        echo "Pasta logs renomeada para logs_${N}"
    else
        echo "Pasta logs não encontrada!"
    fi

    cd build

    echo ""
done

echo "Script finalizado."
