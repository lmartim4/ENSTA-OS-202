# Fire Simulation Project Guide

## Getting Started

To set up and run the fire simulation, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/lmartim4/ENSTA-OS-202.git
```

### 2. Set Up the Virtual Environment
```bash
python3 -m venv tp_parallel
source tp_parallel/bin/activate
```

### 3. Install Dependencies
```bash
cd projet
pip install -r requirements.txt
```

### 4. Build the Project
```bash
mkdir build && cd build && cmake ../ && cd ..
```

## Running the Simulation
To start the loop for varying OpenMP threads and generate the plots, execute:
```bash
./run_simulation.sh
```

### Important Note
Before running the script, you may want to adjust parameters inside `run_simulation.sh`, such as the number of threads, simulation size, or other execution options.

## Script Overview: `run_simulation.sh`
This script performs the following tasks:

1. **Cleans old logs** (if the directory exists).
2. **Builds the project** using CMake.
3. **Runs the simulation** with different numbers of OpenMP threads.
4. **Generates speedup and result plots** using Python.

### Modifications
You may want to modify the following parameters in the script:
- `OMP_NUM_THREADS` values inside the `for` loop.
- Simulation parameters (`-n 1000 -s 500,500`).
- Paths to scripts if needed.

## Output
After execution, the script will generate:
- Logs of the simulations.
- Speedup plots comparing execution times.
- CSV plots showing performance data.

For further customizations, edit the parameters in `run_simulation.sh` accordingly.

---