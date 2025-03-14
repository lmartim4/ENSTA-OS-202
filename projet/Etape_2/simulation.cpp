#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <mpi.h>

#include "model.hpp"
#include "display.hpp"

using namespace std::string_literals;
using namespace std::chrono_literals;

struct ParamsType
{
    double length{1.};
    unsigned discretization{20u};
    std::array<double,2> wind{0.,0.};
    Model::LexicoIndices start{10u,10u};
};

void analyze_arg( int nargs, char* args[], ParamsType& params )
{
    // Argument parsing code unchanged...
    if (nargs ==0) return;
    std::string key(args[0]);
    if (key == "-l"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour la longueur du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.length = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    auto pos = key.find("--longueur=");
    if (pos < key.size())
    {
        auto subkey = std::string(key,pos+11);
        params.length = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-n"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une valeur pour le nombre de cases par direction pour la discrétisation du terrain !" << std::endl;
            exit(EXIT_FAILURE);
        }
        params.discretization = std::stoul(args[1]);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--number_of_cases=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+18);
        params.discretization = std::stoul(subkey);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-w"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la direction du vent !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.wind[0] = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--wind=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+7);
        params.wind[0] = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.wind[1] = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }

    if (key == "-s"s)
    {
        if (nargs < 2)
        {
            std::cerr << "Manque une paire de valeurs pour la position du foyer initial !" << std::endl;
            exit(EXIT_FAILURE);
        }
        std::string values =std::string(args[1]);
        params.start.column = std::stod(values);
        auto pos = values.find(",");
        if (pos == values.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la position du foyer initial" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(values, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-2, &args[2], params);
        return;
    }
    pos = key.find("--start=");
    if (pos < key.size())
    {
        auto subkey = std::string(key, pos+8);
        params.start.column = std::stoul(subkey);
        auto pos = subkey.find(",");
        if (pos == subkey.size())
        {
            std::cerr << "Doit fournir deux valeurs séparées par une virgule pour définir la vitesse" << std::endl;
            exit(EXIT_FAILURE);
        }
        auto second_value = std::string(subkey, pos+1);
        params.start.row = std::stod(second_value);
        analyze_arg(nargs-1, &args[1], params);
        return;
    }
}

ParamsType parse_arguments( int nargs, char* args[] )
{
    if (nargs == 0) return {};
    if ( (std::string(args[0]) == "--help"s) || (std::string(args[0]) == "-h") )
    {
        std::cout << 
R"RAW(Usage : simulation [option(s)]
  Lance la simulation d'incendie en prenant en compte les [option(s)].
  Les options sont :
    -l, --longueur=LONGUEUR     Définit la taille LONGUEUR (réel en km) du carré représentant la carte de la végétation.
    -n, --number_of_cases=N     Nombre n de cases par direction pour la discrétisation
    -w, --wind=VX,VY            Définit le vecteur vitesse du vent (pas de vent par défaut).
    -s, --start=COL,ROW         Définit les indices I,J de la case où commence l'incendie (milieu de la carte par défaut)
)RAW";
        exit(EXIT_SUCCESS);
    }
    ParamsType params;
    analyze_arg(nargs, args, params);
    return params;
}

bool check_params(ParamsType& params)
{
    bool flag = true;
    if (params.length <= 0)
    {
        std::cerr << "[ERREUR FATALE] La longueur du terrain doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if (params.discretization <= 0)
    {
        std::cerr << "[ERREUR FATALE] Le nombre de cellules par direction doit être positive et non nulle !" << std::endl;
        flag = false;
    }

    if ( (params.start.row >= params.discretization) || (params.start.column >= params.discretization) )
    {
        std::cerr << "[ERREUR FATALE] Mauvais indices pour la position initiale du foyer" << std::endl;
        flag = false;
    }
    
    return flag;
}

void display_params(ParamsType const& params)
{
    std::cout << "Parametres définis pour la simulation : \n"
              << "\tTaille du terrain : " << params.length << std::endl 
              << "\tNombre de cellules par direction : " << params.discretization << std::endl 
              << "\tVecteur vitesse : [" << params.wind[0] << ", " << params.wind[1] << "]" << std::endl
              << "\tPosition initiale du foyer (col, ligne) : " << params.start.column << ", " << params.start.row << std::endl;
}

// Structure pour envoyer des données d'affichage entre les processus
struct DisplayData {
    std::vector<unsigned> vegetal_map;
    std::vector<unsigned> fire_map;
    bool continue_simulation;
};

int main(int nargs, char* args[])
{
    // Initialisation de MPI
    MPI_Init(&nargs, &args);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    
    // Vérifier qu'il y a au moins 2 processus
    if (size < 2) {
        if (rank == 0) {
            std::cerr << "Cette implémentation nécessite au moins 2 processus MPI" << std::endl;
        }
        MPI_Finalize();
        return EXIT_FAILURE;
    }
    
    // Tous les processus analysent les arguments
    auto params = parse_arguments(nargs-1, &args[1]);
    
    // Seulement le processus 0 affiche les paramètres
    if (rank == 0) {
        display_params(params);
    }
    
    // Tous les processus vérifient les paramètres
    if (!check_params(params)) {
        MPI_Finalize();
        return EXIT_FAILURE;
    }
    
    // Variables pour mesurer le temps
    double total_time = 0.0;
    int iteration_count = 0;
    
    if (rank == 0) {
        // Processus d'affichage (processus 0)
        auto displayer = Displayer::init_instance(params.discretization, params.discretization);
        
        // Taille des matrices à recevoir
        int map_size = params.discretization * params.discretization;
        
        std::vector<unsigned> vegetal_map(map_size);
        std::vector<unsigned> fire_map(map_size);
        
        MPI_Status status;
        bool continue_simulation = true;
        
        while (continue_simulation) {
            // Recevoir le statut de la simulation du processus 1
            MPI_Recv(&continue_simulation, 1, MPI_C_BOOL, 1, 0, MPI_COMM_WORLD, &status);
            
            if (continue_simulation) {
                // Recevoir les données des cartes
                MPI_Recv(vegetal_map.data(), map_size, MPI_UNSIGNED, 1, 1, MPI_COMM_WORLD, &status);
                MPI_Recv(fire_map.data(), map_size, MPI_UNSIGNED, 1, 2, MPI_COMM_WORLD, &status);
                
                // Recevoir l'étape de temps actuelle
                int time_step;
                MPI_Recv(&time_step, 1, MPI_INT, 1, 3, MPI_COMM_WORLD, &status);
                
                // Afficher les informations si nécessaire
                if ((time_step & 31) == 0) {
                    std::cout << "Time step " << time_step << "\n===============" << std::endl;
                }
                
                // Mettre à jour l'affichage
                displayer->update(vegetal_map, fire_map);
                
                // Vérifier si l'utilisateur souhaite quitter
                SDL_Event event;
                bool quit = false;
                if (SDL_PollEvent(&event) && event.type == SDL_QUIT) {
                    quit = true;
                }
                
                // Envoyer le signal de quitter au processus de calcul
                MPI_Send(&quit, 1, MPI_C_BOOL, 1, 4, MPI_COMM_WORLD);
                
                // Pause pour l'affichage
                std::this_thread::sleep_for(0.1s);
            }
        }
        
        // Recevoir le temps de calcul moyen
        MPI_Recv(&total_time, 1, MPI_DOUBLE, 1, 5, MPI_COMM_WORLD, &status);
        MPI_Recv(&iteration_count, 1, MPI_INT, 1, 6, MPI_COMM_WORLD, &status);
        
        // Afficher les résultats de temps
        if (iteration_count > 0) {
            double avg_time = total_time / iteration_count;
            std::cout << "Temps total de calcul: " << total_time << " secondes" << std::endl;
            std::cout << "Nombre d'itérations: " << iteration_count << std::endl;
            std::cout << "Temps moyen par itération: " << avg_time << " secondes" << std::endl;
        }
    }
    else if (rank == 1) {
        // Processus de calcul (processus 1)
        auto simu = Model(params.length, params.discretization, params.wind, params.start);
        
        // Taille des matrices à envoyer
        int map_size = params.discretization * params.discretization;
        
        bool continue_simulation = true;
        bool quit = false;
        MPI_Status status;
        
        // Chronomètre pour mesurer le temps de calcul
        auto start_time = std::chrono::high_resolution_clock::now();
        
        while (continue_simulation && !quit) {
            // Mesurer le temps de cette itération
            auto iter_start = std::chrono::high_resolution_clock::now();
            
            // Mettre à jour la simulation
            continue_simulation = simu.update();
            
            // Mesurer le temps de fin d'itération
            auto iter_end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> iter_duration = iter_end - iter_start;
            total_time += iter_duration.count();
            iteration_count++;
            
            // Envoyer le statut de la simulation au processus 0
            MPI_Send(&continue_simulation, 1, MPI_C_BOOL, 0, 0, MPI_COMM_WORLD);
            
            if (continue_simulation) {
                // Obtenir les cartes actuelles
                auto vegetal_map = simu.vegetal_map();
                auto fire_map = simu.fire_map();
                
                // Obtenir l'étape de temps actuelle
                int time_step = simu.time_step();
                
                // Envoyer les données au processus d'affichage
                MPI_Send(vegetal_map.data(), map_size, MPI_UNSIGNED, 0, 1, MPI_COMM_WORLD);
                MPI_Send(fire_map.data(), map_size, MPI_UNSIGNED, 0, 2, MPI_COMM_WORLD);
                MPI_Send(&time_step, 1, MPI_INT, 0, 3, MPI_COMM_WORLD);
                
                // Recevoir si l'utilisateur souhaite quitter
                MPI_Recv(&quit, 1, MPI_C_BOOL, 0, 4, MPI_COMM_WORLD, &status);
            }
        }
        
        // Envoyer les statistiques de temps au processus 0
        MPI_Send(&total_time, 1, MPI_DOUBLE, 0, 5, MPI_COMM_WORLD);
        MPI_Send(&iteration_count, 1, MPI_INT, 0, 6, MPI_COMM_WORLD);
    }
    
    // Finaliser MPI
    MPI_Finalize();
    return EXIT_SUCCESS;
}