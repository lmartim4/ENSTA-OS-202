#include <string>
#include <cstdlib>
#include <cassert>
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <ctime>
#include <omp.h>
#include <filesystem>
#include "model.hpp"
#include "display.hpp"

using namespace std::string_literals;
using namespace std::chrono_literals;

struct ParamsType
{
    double length{1.};
    unsigned discretization{20u};
    std::array<double,2> wind{0.,0.};
    Model::Coordinates start{10u,10u};
};

void analyze_arg( int nargs, char* args[], ParamsType& params )
{
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
        params.wind[0] = std::stod(subkey);
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

std::string generate_timestamp_filename()
{
    auto now = std::chrono::system_clock::now();
    std::time_t now_time = std::chrono::system_clock::to_time_t(now);
    std::tm local_tm = *std::localtime(&now_time);

    std::ostringstream oss;
    oss << std::put_time(&local_tm, "%H-%M-%S-%d-%m-%Y") << ".csv";
    return oss.str();
}

int main( int nargs, char* args[] )
{
    auto params = parse_arguments(nargs-1, &args[1]);
    display_params(params);
    if (!check_params(params)) return EXIT_FAILURE;

    auto displayer = Displayer::init_instance(params.discretization, params.discretization);
    auto simu = Model(params.length, params.discretization, params.wind, params.start);
    SDL_Event event;


    std::filesystem::create_directories("logs");

    std::ofstream csv_file("logs/" + generate_timestamp_filename());
    if (!csv_file.is_open())
    {
        std::cerr << "Unable to open CSV file" << std::endl;
        return EXIT_FAILURE;
    }

    csv_file << "Taille du terrain : " << params.length << std::endl 
    << "Nombre de cellules par direction : " << params.discretization << std::endl 
    << "Vecteur vitesse : [" << params.wind[0] << ", " << params.wind[1] << "]" << std::endl
    << "Position initiale du foyer (col, ligne) : " << params.start.column << ", " << params.start.row << std::endl;

    
    int num_threads = omp_get_max_threads();
    csv_file << "OpenMP threads: " << num_threads << "\n";
    csv_file << "step,update_time,display_time,total_time\n";


    while (true)
    {
        auto iter_start = std::chrono::high_resolution_clock::now();

        auto update_start = std::chrono::high_resolution_clock::now();
        bool updating = simu.update();
        auto update_end = std::chrono::high_resolution_clock::now();

        if (!updating)
            break;  // Exit if simulation update returns false.

        while (SDL_PollEvent(&event))
            if (event.type == SDL_QUIT)
                return EXIT_SUCCESS;
        
        auto display_start = std::chrono::high_resolution_clock::now();
        displayer->update(simu.vegetal_map(), simu.get_fire_map());
        auto display_end = std::chrono::high_resolution_clock::now();

        auto iter_end = std::chrono::high_resolution_clock::now();

        auto update_time = std::chrono::duration_cast<std::chrono::microseconds>(update_end - update_start).count();
        auto display_time = std::chrono::duration_cast<std::chrono::microseconds>(display_end - display_start).count();
        auto total_time = std::chrono::duration_cast<std::chrono::microseconds>(iter_end - iter_start).count();
        
        if ((simu.get_time_step() & 31) == 0)
            std::cout << "Time step " << simu.get_time_step() << "\n===============" << std::endl;

        csv_file << simu.get_time_step()-1 << "," << update_time << "," << display_time << "," << total_time << "\n";

    }
    
    csv_file.close();    
    return EXIT_SUCCESS;
}