#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <mpi.h>

#include "model.hpp"
#include "display.hpp"
#include "profiler.hpp"

constexpr int UPDATE_RANK   = 1;
constexpr int DISPLAY_RANK  = 0;

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


int main(int argc, char* argv[])
{
    MPI_Init(&argc, &argv);

    int rank = 0, size = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    auto params = parse_arguments(argc - 1, &argv[1]);
    if (!check_params(params))
    {
        MPI_Abort(MPI_COMM_WORLD, EXIT_FAILURE);
        return EXIT_FAILURE;
    }

    if (rank == UPDATE_RANK)
    {
        display_params(params);
        std::cout << "Running with " << size << " process(es)\n";
    }

    Profiler profiler("rank" + std::to_string(rank), "Profiling data for rank " + std::to_string(rank) + " of " + std::to_string(size)  + "\n");

    if (rank == UPDATE_RANK)
    {
        Model simulation(params.length, params.discretization, params.wind, params.start);

        int iteration_count = 0;
        double total_time_accumulator = 0.0;

        while (true)
        {
            profiler.start("total");

            auto iteration_begin = std::chrono::high_resolution_clock::now();

            profiler.start("update");
            bool running = simulation.update();
            profiler.stop("update");

            MPI_Send(&running, 1, MPI_C_BOOL, DISPLAY_RANK, 0, MPI_COMM_WORLD);

            if (!running)
            {
                profiler.stop("total");
                break;
            }

            const auto &veg_map = simulation.vegetal_map();
            MPI_Send(veg_map.data(),
                     veg_map.size(),
                     MPI_UNSIGNED_CHAR,
                     DISPLAY_RANK, 0,
                     MPI_COMM_WORLD);

            const auto &fire_map = simulation.fire_map();
            MPI_Send(fire_map.data(),
                     fire_map.size(),
                     MPI_UNSIGNED_CHAR,
                     DISPLAY_RANK, 0,
                     MPI_COMM_WORLD);

            profiler.stop("total");

            profiler.log(simulation.time_step());

            auto iteration_end   = std::chrono::high_resolution_clock::now();
            auto elapsed_in_us   = std::chrono::duration_cast<std::chrono::microseconds>(
                                       iteration_end - iteration_begin
                                   ).count();
            double elapsed_in_ms = static_cast<double>(elapsed_in_us) / 1000.0;

            total_time_accumulator += elapsed_in_ms;
            iteration_count++;
        }

        if (iteration_count > 0)
        {
            double average_ms = total_time_accumulator / iteration_count;
            std::cout << "\n[Rank " << rank << "]"
                      << " Average iteration time: "
                      << average_ms << " ms\n";
        }
    }

    else if (rank == DISPLAY_RANK)
    {
        auto displayer = Displayer::init_instance(
            params.discretization,
            params.discretization
        );

        bool running = true;
        int step = 0;

        while (running)
        {
            profiler.start("total");
 
            MPI_Recv(&running, 1, MPI_C_BOOL, UPDATE_RANK, 0,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            if (!running)
            {
                profiler.stop("total");
                break;
            }

            std::vector<std::uint8_t> vegetation(params.discretization * params.discretization);
            MPI_Recv(vegetation.data(),
                     vegetation.size(),
                     MPI_UNSIGNED_CHAR,
                     UPDATE_RANK, 0,
                     MPI_COMM_WORLD,
                     MPI_STATUS_IGNORE);

            std::vector<std::uint8_t> fire(params.discretization * params.discretization);
            MPI_Recv(fire.data(),
                     fire.size(),
                     MPI_UNSIGNED_CHAR,
                     UPDATE_RANK, 0,
                     MPI_COMM_WORLD,
                     MPI_STATUS_IGNORE);

            profiler.start("display");
            displayer->update(vegetation, fire);
            profiler.stop("display");

            profiler.stop("total");
            profiler.log(step++);
        }
    }

    MPI_Finalize();
    return 0;
}