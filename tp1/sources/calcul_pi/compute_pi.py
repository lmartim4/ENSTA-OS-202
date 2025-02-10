from mpi4py import MPI
import numpy as np
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

nb_samples_total = 100_000_000

samples_per_process = nb_samples_total // size
reste = nb_samples_total % size
if rank < reste:
    samples_per_process += 1

if rank == 0:
    start_time = time.time()

x = 2.0 * np.random.random_sample(samples_per_process) - 1.0
y = 2.0 * np.random.random_sample(samples_per_process) - 1.0

local_count = np.sum(x*x + y*y < 1)

global_count = comm.reduce(local_count, op=MPI.SUM, root=0)

if rank == 0:
    approx_pi = 4.0 * global_count / nb_samples_total
    end_time = time.time()
    print(f"Temps pour calculer pi : {end_time - start_time} secondes")
    print(f"Pi vaut environ {approx_pi}")
