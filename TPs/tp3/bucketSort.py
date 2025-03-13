import numpy as np
from mpi4py import MPI

def bucket_sort(sequence, nbp):
    """Sorts the sequence using Bucket Sort with nbp buckets."""
    # Determine bucket range
    min_val, max_val = min(sequence), max(sequence)
    range_size = (max_val - min_val) / nbp

    # Create empty buckets
    buckets = [[] for _ in range(nbp)]

    # Assign elements to corresponding buckets
    for num in sequence:
        index = min(int((num - min_val) / range_size), nbp - 1)
        buckets[index].append(num)

    # Sort each bucket individually
    sorted_buckets = [sorted(bucket) for bucket in buckets]

    # Flatten sorted buckets
    sorted_sequence = [num for bucket in sorted_buckets for num in bucket]
    return sorted_sequence

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    nbp = size  # Number of buckets equal to the number of processes
    data_size = 100  # Total numbers to sort

    if rank == 0:
        # Generate random sequence
        sequence = np.random.randint(0, 32768, size=data_size,dtype=np.int32)

        # Divide data among processes
        chunk_size = len(sequence) // size
        chunks = [sequence[i * chunk_size : (i + 1) * chunk_size] for i in range(size)]
    else:
        chunks = None

    # Scatter data across processes
    local_data = comm.scatter(chunks, root=0)

    # Each process sorts its bucket
    local_sorted = sorted(local_data)

    # Gather sorted buckets at rank 0
    sorted_chunks = comm.gather(local_sorted, root=0)

    if rank == 0:
        # Flatten and merge sorted chunks
        sorted_sequence = [num for chunk in sorted_chunks for num in chunk]
        print("Sorted sequence:", sorted_sequence)

if __name__ == "__main__":
    main()