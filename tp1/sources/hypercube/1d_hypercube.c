#include <stdio.h>
#include <mpi.h>

int main(int argc, char *argv[])
{
    int rank, token;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if (rank == 0)
    {
        token = 99;
        MPI_Send(&token, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        printf("Task 0: Eu envio %d\n", token);
    }
    else if (rank == 1)
    {
        MPI_Recv(&token, 1, MPI_INT,0,0,MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Tâche 1 : Eu recebo = %d\n", token);
    }

    MPI_Finalize();
    return 0;
}
