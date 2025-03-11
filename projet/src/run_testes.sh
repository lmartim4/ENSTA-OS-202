#!/bin/bash

rm -rf logs/*

make clean && make simulation.exe 

for threads in {1..4}; do
    export OMP_NUM_THREADS=$threads
    echo "Running simulation with OMP_NUM_THREADS=$OMP_NUM_THREADS"

    ./simulation.exe -n 700 -s 350,350
done

for csv_file in logs/*.csv; do
    [ -e "$csv_file" ] || continue
    python csv_plot.py "$csv_file"
done

python speedup_plot.py
