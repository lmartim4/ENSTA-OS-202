import numpy as np
from mpi4py import MPI
import argparse

def generate_data(dim):
    A = np.array([[(i + j) % dim + 2. for i in range(dim)] for j in range(dim)])
    u = np.array([i + 1. for i in range(dim)])
    return A, u

def test_row_multiplication(alpha):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nbp = comm.Get_size()

    if rank == 0:
        dim = nbp * alpha
        A, u = generate_data(dim)
        expected = A.dot(u)
        A_chunks = np.array_split(A, nbp, axis=0)
    else:
        u = None
        A_chunks = None
        expected = None

    u = comm.bcast(u, root=0)
    A_local = comm.scatter(A_chunks, root=0)

    comm.Barrier()
    t_start = MPI.Wtime()

    prod_local = A_local.dot(u)

    t_end = MPI.Wtime()
    local_time = t_end - t_start
    total_time = comm.reduce(local_time, op=MPI.MAX, root=0)

    prod_list = comm.gather(prod_local, root=0)

    if rank == 0:
        prod_complete = np.concatenate(prod_list)
        print(f"Row-wise of {nbp}x{alpha}={dim} multiplication took {total_time:.6f} seconds.")
        if not np.allclose(expected, prod_complete):
            print("Failed")

def test_col_multiplication(alpha):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nbp = comm.Get_size()

    if rank == 0:
        dim = nbp * alpha
        A, u = generate_data(dim)
        expected = A.dot(u)
        A_chunks = np.array_split(A, nbp, axis=1)
        U_chunks = np.array_split(u, nbp)
    else:
        A_chunks = None
        U_chunks = None
        expected = None

    A_local = comm.scatter(A_chunks, root=0)
    u_local = comm.scatter(U_chunks, root=0)

    comm.Barrier()
    t_start = MPI.Wtime()

    prod_local = A_local.dot(u_local)

    prod_complete = None
    if rank == 0:
        prod_complete = np.empty_like(prod_local)
    comm.Reduce(prod_local, prod_complete, op=MPI.SUM, root=0)

    t_end = MPI.Wtime()
    local_time = t_end - t_start
    total_time = comm.reduce(local_time, op=MPI.MAX, root=0)

    if rank == 0:
        print(f"Column-wise of {nbp}x{alpha}={dim} multiplication took {total_time:.6f} seconds.")
        if not np.allclose(expected, prod_complete):
            print("Failed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=int, default=1024)
    args = parser.parse_args()
    alpha = args.alpha

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    test_row_multiplication(alpha)
    comm.Barrier()
    test_col_multiplication(alpha)

if __name__ == "__main__":
    main()
