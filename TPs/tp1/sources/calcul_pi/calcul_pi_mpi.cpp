#include <chrono>
#include <random>
#include <cstdlib>
#include <sstream>
#include <string>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <mpi.h>

int main(int argc, char* argv[])
{
    // Initialisation de MPI
    MPI_Init(&argc, &argv);
    MPI_Comm globComm;
    MPI_Comm_dup(MPI_COMM_WORLD, &globComm);

    // Récupération du nombre de processus et du rang du processus courant
    int nbp, rank;
    MPI_Comm_size(globComm, &nbp);
    MPI_Comm_rank(globComm, &rank);

    // Nombre total d'échantillons (darts) pour la simulation.
    // On peut le préciser en argument (par exemple : ./prog 100000000)
    unsigned long totalSamples = 100000000; // valeur par défaut
    if (argc > 1)
        totalSamples = std::stoul(argv[1]);

    // Répartition des échantillons entre processus
    unsigned long localSamples = totalSamples / nbp;

    // (Optionnel) Création d'un fichier de sortie pour ce processus
    std::stringstream fileName;
    fileName << "Output" << std::setfill('0') << std::setw(5) << rank << ".txt";
    std::ofstream output(fileName.str().c_str());

    // Mesure du temps d'exécution : début
    double t0 = MPI_Wtime();

    // Chaque processus réalise sa part de la simulation
    unsigned long localCount = 0; // nombre de points dans le disque unité
    // Pour obtenir des graines différentes, on combine le temps et le rang
    unsigned seed = static_cast<unsigned>(
                        std::chrono::high_resolution_clock::now()
                        .time_since_epoch().count()) + rank;
    std::default_random_engine generator(seed);
    std::uniform_real_distribution<double> distribution(-1.0, 1.0);

    for (unsigned long i = 0; i < localSamples; ++i) {
        double x = distribution(generator);
        double y = distribution(generator);
        if (x * x + y * y <= 1.0)
            localCount++;
    }

    // Réduction : somme des points dans le disque sur tous les processus
    unsigned long globalCount = 0;
    MPI_Reduce(&localCount, &globalCount, 1, MPI_UNSIGNED_LONG, MPI_SUM, 0, globComm);

    // Mesure du temps d'exécution : fin
    double t1 = MPI_Wtime();
    double localTime = t1 - t0;

    // On récupère le temps maximum parmi tous les processus (le temps global)
    double maxTime;
    MPI_Reduce(&localTime, &maxTime, 1, MPI_DOUBLE, MPI_MAX, 0, globComm);

    // Le processus racine calcule l'approximation de pi et affiche les résultats
    if (rank == 0) {
        // Le nombre total d'échantillons utilisés (en général : totalSamples)
        unsigned long usedSamples = localSamples * nbp;
        double pi = 4.0 * static_cast<double>(globalCount) / static_cast<double>(usedSamples);
        std::cout << "Approximation de pi = " << pi << std::endl;
        std::cout << "Nombre total d'echantillons = " << usedSamples << std::endl;
        std::cout << "Temps d'execution (s) = " << maxTime << std::endl;
    }

    // (Optionnel) Écriture d'un rapport dans le fichier de sortie local
    output << "Processus " << rank 
           << " : " << localCount << " points dans le disque sur " 
           << localSamples << " lancers." << std::endl;
    output << "Temps d'execution (s) = " << localTime << std::endl;
    output.close();

    MPI_Finalize();
    return EXIT_SUCCESS;
}
