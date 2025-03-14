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

### Details Processuer

Le projet a été simulé dans ce processeur ci-dessous:

| Category | Value |
|----------|-------|
| Architecture | x86_64 |
| CPU op-mode(s) | 32-bit, 64-bit |
| Address sizes | 43 bits physical, 48 bits virtual |
| Byte Order | Little Endian |
| CPU(s) | 12 |
| On-line CPU(s) list | 0-11 |
| Vendor ID | AuthenticAMD |
| Model name | AMD Ryzen 5 3600X 6-Core Processor |
| CPU family | 23 |
| Model | 113 |
| Thread(s) per core | 2 |
| Core(s) per socket | 6 |
| Socket(s) | 1 |
| Stepping | 0 |
| Frequency boost | enabled |
| CPU(s) scaling MHz | 48% |
| CPU max MHz | 4409.0000 |
| CPU min MHz | 550.0000 |
| BogoMIPS | 7602.42 |
| Flags | fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid extd_apicid aperfmperf rapl pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs skinit wdt tce topoext perfctr_core perfctr_nb bpext perfctr_llc mwaitx cpb cat_l3 cdp_l3 hw_pstate ssbd mba ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 cqm rdt_a rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local clzero irperf xsaveerptr rdpru wbnoinvd arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold avic v_vmsave_vmload vgif v_spec_ctrl umip rdpid overflow_recov succor smca sev sev_es |
| **Virtualization features** | |
| Virtualization | AMD-V |
| **Caches (sum of all)** | |
| L1d | 192 KiB (6 instances) |
| L1i | 192 KiB (6 instances) |
| L2 | 3 MiB (6 instances) |
| L3 | 32 MiB (2 instances) |
| **NUMA** | |
| NUMA node(s) | 1 |
| NUMA node0 CPU(s) | 0-11 |
| **Vulnerabilities** | |
| Gather data sampling | Not affected |
| Itlb multihit | Not affected |
| L1tf | Not affected |
| Mds | Not affected |
| Meltdown | Not affected |
| Mmio stale data | Not affected |
| Reg file data sampling | Not affected |
| Retbleed | Mitigation; untrained return thunk; SMT enabled with STIBP protection |
| Spec rstack overflow | Mitigation; Safe RET |
| Spec store bypass | Mitigation; Speculative Store Bypass disabled via prctl |
| Spectre v1 | Mitigation; usercopy/swapgs barriers and __user pointer sanitization |
| Spectre v2 | Mitigation; Retpolines; IBPB conditional; STIBP always-on; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected |
| Srbds | Not affected |
| Tsx async abort | Not affected |