#include <stdio.h>
#include <mpi.h>

int main(int argc, char *argv[]) {
    int nbp, rank, token;
    MPI_Status status;

    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &nbp);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if (nbp < 2) {
        if (rank == 0) 
            fprintf(stderr, "Need at least 2 cores\n");
        
        MPI_Finalize();
        return 1;
    }

    if (rank == 0) {
        token = 1;
        MPI_Send(&token, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        MPI_Recv(&token, 1, MPI_INT, nbp - 1, 0, MPI_COMM_WORLD, &status);
        printf("Process 0 got %d\n", token);
    } else {
        MPI_Recv(&token, 1, MPI_INT, rank - 1, 0, MPI_COMM_WORLD, &status);
        printf("Process %d got %d\n",rank, token);
        token++;
        int dest = (rank == nbp - 1) ? 0 : rank + 1;
        MPI_Send(&token, 1, MPI_INT, dest, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
}
