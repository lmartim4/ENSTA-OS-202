#!/bin/bash

trap "echo 'Process interrupted. Exiting...'; exit 1" SIGINT SIGTERM

BUILD_DIR="build"
LOG_DIR="logs"
MPI_PROCS=2  # Adjust as needed

if [ -d "$LOG_DIR" ]; then
    echo "Cleaning old logs..."
    rm -rf "$LOG_DIR"/*
else
    echo "Creating log directory..."
    mkdir -p "$LOG_DIR"
fi

cd "$BUILD_DIR" || { echo "Build directory not found! (create build and run \"cmake ..\" there)"; exit 1; }

echo "Compiling the project..."
cmake --build .

if [ ! -f "./simulation.exe" ]; then
    echo "Error: Compilation failed or simulation.exe not found!"
    exit 1
fi

# Run for different values of N
for N in 50 100 200 400; do
    echo "Running tests for N=$N"
    echo "========================================"

    HALF_N=$((N/2))

    # Loop over desired OpenMP thread counts
    for threads in 1 2 4 6 10; do
        echo "Running 5 trials with $MPI_PROCS MPI processes and OMP_NUM_THREADS=$threads"
        for i in {1..5}; do
            echo "Trial $i with MPI=$MPI_PROCS and OMP_NUM_THREADS=$threads"
            export OMP_NUM_THREADS=$threads
            mpirun -np $MPI_PROCS --bind-to none ./simulation.exe -n $N -s $HALF_N,$HALF_N
            echo "----------------------------------------"
        done

        # Move back one level to run plotting scripts
        cd ..

        echo "Generating graphs for N=$N, OMP_NUM_THREADS=$threads..."
        python speedup_plot.py
        python csv_plot.py

        # Create benchmark directory that encodes N and thread count
        BENCHMARK_DIR="benchmark_${N}_omp${threads}"
        echo "Creating $BENCHMARK_DIR directory..."
        mkdir -p "$BENCHMARK_DIR"

        # Move plot folder into benchmark directory
        if [ -d "plots" ]; then
            echo "Moving plot folder to $BENCHMARK_DIR directory..."
            mv plots "$BENCHMARK_DIR/"
        else
            echo "Warning: plots folder not found for N=$N, OMP_NUM_THREADS=$threads"
        fi

        # Move logs to benchmark directory
        if [ -d "$LOG_DIR" ]; then
            echo "Moving logs to $BENCHMARK_DIR directory..."
            mv "$LOG_DIR" "$BENCHMARK_DIR/"

            # Recreate empty logs directory for next iteration
            echo "Creating fresh logs directory for next run..."
            mkdir -p "$LOG_DIR"
        else
            echo "Warning: log directory not found"
        fi

        # Return to the build directory for the next iteration
        cd "$BUILD_DIR"
    done

done

echo "Process completed!"
