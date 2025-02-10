#include <chrono>
#include <random>
#include <cstdlib>
#include <sstream>
#include <string>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <omp.h>

// Attention , ne marche qu'en C++ 11 ou supérieur :
double approximate_pi(unsigned long nbSamples) {
    unsigned long nbDarts = 0;

    // Create a parallel region
    #pragma omp parallel
    {
        // Each thread gets its own random generator instance to avoid collisions.
        unsigned int seed = static_cast<unsigned int>(
            std::chrono::high_resolution_clock::now().time_since_epoch().count() + omp_get_thread_num()
        );
        std::default_random_engine generator(seed);
        std::uniform_real_distribution<double> distribution(-1.0, 1.0);

        // Distribute the loop iterations among threads, with a reduction on nbDarts.
        #pragma omp for reduction(+:nbDarts)
        for (unsigned long sample = 0; sample < nbSamples; ++sample) {
            double x = distribution(generator);
            double y = distribution(generator);
            if (x * x + y * y <= 1.0)
                nbDarts++;
        }
    }

    double ratio = static_cast<double>(nbDarts) / static_cast<double>(nbSamples);
    return 4.0 * ratio;
}

int main(int argc, char *argv[])
{
    // Par défaut, on utilise 100 millions de tirages, modifiable en ligne de commande.
    unsigned long nbSamples = 100000000;
    if (argc > 1)
    {
        nbSamples = std::stoul(argv[1]);
    }

    // On peut aussi modifier le nombre de threads via la ligne de commande.
    // Si le second argument est fourni, on force le nombre de threads.
    if (argc > 2)
    {
        int nThreads = std::stoi(argv[2]);
        omp_set_num_threads(nThreads);
    }

    int usedThreads = omp_get_max_threads();
    std::cout << "Utilisation de " << usedThreads << " threads." << std::endl;
    std::cout << "Nombre d'échantillons : " << nbSamples << std::endl;

    auto start = std::chrono::high_resolution_clock::now();
    double pi = approximate_pi(nbSamples);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;

    std::cout << std::setprecision(15);
    std::cout << "Valeur approchée de pi : " << pi << std::endl;
    std::cout << "Temps d'exécution   : " << elapsed.count() << " s" << std::endl;

    return EXIT_SUCCESS;
}