#pragma once
#include <cstdint>
#include <array>
#include <vector>
#include <unordered_map>

class Model
{
public:
    struct Coordinates
    {
        unsigned row, column;
    };

    Model( double t_length, unsigned t_discretization, std::array<double,2> t_wind,
           Coordinates t_start_fire_position, double t_max_wind = 60. );
    Model( Model const & ) = delete;
    Model( Model      && ) = delete;
    ~Model() = default;

    Model& operator = ( Model const & ) = delete;
    Model& operator = ( Model      && ) = delete;

    bool update();

    unsigned get_geometry() const { return geometry; }
    std::vector<std::uint8_t> vegetal_map() const { return vegetation_map; }
    std::vector<std::uint8_t> get_fire_map() const { return fire_map; }
    std::size_t get_time_step() const { return time_step; }

private:
    std::size_t   get_index_from_coord( Coordinates t_lexico_indices  ) const;
    Coordinates get_coord_from_index        ( std::size_t t_global_index ) const;

    double length;                    // Taille du carré représentant le terrain (en km)
    double distance;                  // Taille d'une case du terrain modélisé
    std::size_t time_step = 0;        // Dernier numéro du pas de temps calculé
    unsigned geometry;                // Taille en nombre de cases de la carte 2D
    std::array<double,2> wind{0.,0.}; // Vitesse et direction du vent suivant les axes x et y en km/h
    double wind_speed;                // Norme euclidienne de la vitesse du vent
    double max_wind;                  //+ Vitesse à partir de laquelle le feu ne peut pas se propager dans le sens opposé à celui du vent.
    std::vector<std::uint8_t> vegetation_map, fire_map;
    double p1{0.}, p2{0.};
    double alphaEastWest, alphaWestEast, alphaSouthNorth, alphaNorthSouth;

    std::unordered_map<std::size_t, std::uint8_t> fire_front;
};
