#!/bin/bash

# Loop from 1 to 12
for threads in {1..12}; do
    export OMP_NUM_THREADS=$threads
    echo "Running simulation with OMP_NUM_THREADS=$OMP_NUM_THREADS"
    
    # Clean, compile, and execute the simulation
    make clean && make simulation.exe && ./simulation.exe -n 300 -s 150,150

    echo "Finished run with OMP_NUM_THREADS=$OMP_NUM_THREADS"
    echo "--------------------------------------"
done
