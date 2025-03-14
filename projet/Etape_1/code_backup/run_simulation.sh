#!/bin/bash

trap "echo 'Process interrupted. Exiting...'; exit 1" SIGINT SIGTERM

BUILD_DIR="build"
LOG_DIR="logs"

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
for N in 50 100 200 400 700 1000; do
    echo "Running tests for N=$N"
    echo "========================================"
    
    HALF_N=$((N/2))
    
    for i in {1..5}; do
        for threads in {1..12}; do
            echo "Running with OMP_NUM_THREADS=$threads"
            export OMP_NUM_THREADS=$threads
            ./simulation.exe -n $N -s $HALF_N,$HALF_N
            echo "----------------------------------------"
        done
    done
    
    cd ..
    
    echo "Generating graphs for N=$N..."
    python speedup_plot.py
    python csv_plot.py
    
    # Create benchmark_N directory
    echo "Creating benchmark_$N directory..."
    mkdir -p "benchmark_$N"
    
    # Move plot folder to benchmark_N
    if [ -d "plots" ]; then
        echo "Moving plot folder to benchmark_$N directory..."
        mv plots "benchmark_$N/"
    else
        echo "Warning: plots folder not found for N=$N"
    fi
    
    # Move logs to benchmark_N folder
    if [ -d "$LOG_DIR" ]; then
        echo "Moving logs to benchmark_$N directory..."
        mv "$LOG_DIR" "benchmark_$N/"
        
        
        # Recreate empty logs directory for next run
        echo "Creating fresh logs directory for next run..."
        mkdir -p "$LOG_DIR"
    else
        echo "Warning: log directory not found"
    fi
    
    # Go back to build directory for the next iteration
    cd "$BUILD_DIR"
done

echo "Process completed!"
