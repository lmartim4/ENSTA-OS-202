#include <stdexcept>
#include <cmath>
#include <iostream>
#include "model.hpp"
#include <omp.h>
#include <algorithm>

namespace
{
    double pseudo_random(std::size_t index, std::size_t time_step)
    {
        // Multiply index*((time_step+1) + 10000) removes
        std::uint_fast32_t xi = std::uint_fast32_t(index * (10000 + time_step + 1));
        std::uint_fast32_t r = (48271 * xi) % 2147483647;
        return r / 2147483646.;
    }

    double log_factor(std::uint8_t value)
    {
        return std::log(1. + value) / std::log(256);
    }
}

Model::Model(double t_length, unsigned t_discretization, std::array<double, 2> t_wind,
             Coordinates t_start_fire_position, double t_max_wind)
    : length(t_length),
      distance(-1),
      geometry(t_discretization),
      wind(t_wind),
      wind_speed(std::sqrt(t_wind[0] * t_wind[0] + t_wind[1] * t_wind[1])),
      max_wind(t_max_wind),
      vegetation_map(t_discretization * t_discretization, 255u),
      fire_map(t_discretization * t_discretization, 0u)
{
    if (t_discretization == 0)
        throw std::range_error("Le nombre de cases par direction doit être plus grand que zéro.");

    distance = length / double(geometry);
    auto index = get_index_from_coord(t_start_fire_position);
    fire_map[index] = 255u;
    fire_front[index] = 255u;

    constexpr double alpha0 = 4.52790762e-01;
    constexpr double alpha1 = 9.58264437e-04;
    constexpr double alpha2 = 3.61499382e-05;

    if (wind_speed < t_max_wind)
        p1 = alpha0 + alpha1 * wind_speed + alpha2 * (wind_speed * wind_speed);
    else
        p1 = alpha0 + alpha1 * t_max_wind + alpha2 * (t_max_wind * t_max_wind);

    p2 = 0.3;

    if (wind[0] > 0)
    {
        alphaEastWest = std::abs(wind[0] / t_max_wind) + 1;
        alphaWestEast = 1. - std::abs(wind[0] / t_max_wind);
    }
    else
    {
        alphaWestEast = std::abs(wind[0] / t_max_wind) + 1;
        alphaEastWest = 1. - std::abs(wind[0] / t_max_wind);
    }

    if (wind[1] > 0)
    {
        alphaSouthNorth = std::abs(wind[1] / t_max_wind) + 1;
        alphaNorthSouth = 1. - std::abs(wind[1] / t_max_wind);
    }
    else
    {
        alphaNorthSouth = std::abs(wind[1] / t_max_wind) + 1;
        alphaSouthNorth = 1. - std::abs(wind[1] / t_max_wind);
    }
}

bool Model::update()
{
    auto next_front = fire_front;
    
    // Instead of copying keys and intensities to separate vectors, we create a vector
    // of iterators to the fire_front elements. This assumes that fire_front supports iteration.
    std::vector<decltype(fire_front.begin())> front_iters;
    front_iters.reserve(fire_front.size());
    for (auto it = fire_front.begin(); it != fire_front.end(); ++it)
    {
        front_iters.push_back(it);
    }
    
    struct LocalUpdate {
        std::size_t index;
        uint8_t value;
        bool is_new;
    };
    
    std::vector<std::vector<LocalUpdate>> all_local_updates;
    
    #pragma omp parallel
    {
        #pragma omp single
        {
            all_local_updates.resize(omp_get_num_threads());
        }
        
        int thread_id = omp_get_thread_num();
        auto& local_updates = all_local_updates[thread_id];
        local_updates.reserve(front_iters.size() * 4);
        
        #pragma omp for schedule(dynamic, 64)
        for (std::size_t i = 0; i < front_iters.size(); i++)
        {
            // Directly get the key and value from the iterator.
            const auto& fire_pair = *front_iters[i];
            std::size_t current_index = fire_pair.first;
            uint8_t current_intensity = fire_pair.second;
            
            Coordinates coord = get_coord_from_index(current_index);
            double power = log_factor(current_intensity);
            
            // Check south
            if (coord.row < geometry - 1)
            {
                double tirage = pseudo_random(current_index + time_step, time_step);
                double green_power = vegetation_map[current_index + geometry];
                double correction = power * log_factor(green_power);
                if (tirage < alphaSouthNorth * p1 * correction)
                {
                    local_updates.push_back({current_index + geometry, 255, true});
                }
            }
            
            // Check north
            if (coord.row > 0)
            {
                double tirage = pseudo_random(current_index * 13427 + time_step, time_step);
                double green_power = vegetation_map[current_index - geometry];
                double correction = power * log_factor(green_power);
                if (tirage < alphaNorthSouth * p1 * correction)
                {
                    local_updates.push_back({current_index - geometry, 255, true});
                }
            }
            
            // Check east
            if (coord.column < geometry - 1)
            {
                double tirage = pseudo_random(current_index * 13427 * 13427 + time_step, time_step);
                double green_power = vegetation_map[current_index + 1];
                double correction = power * log_factor(green_power);
                if (tirage < alphaEastWest * p1 * correction)
                {
                    local_updates.push_back({current_index + 1, 255, true});
                }
            }
            
            // Check west
            if (coord.column > 0)
            {
                double tirage = pseudo_random(current_index * 13427 * 13427 * 13427 + time_step, time_step);
                double green_power = vegetation_map[current_index - 1];
                double correction = power * log_factor(green_power);
                if (tirage < alphaWestEast * p1 * correction)
                {
                    local_updates.push_back({current_index - 1, 255, true});
                }
            }
            
            // Handle current cell fire decay
            if (current_intensity == 255)
            {
                double tirage = pseudo_random(current_index * 52513 + time_step, time_step);
                if (tirage < p2)
                {
                    uint8_t new_intensity = current_intensity >> 1;
                    local_updates.push_back({current_index, new_intensity, false});
                }
            }
            else
            {
                uint8_t new_intensity = current_intensity >> 1;
                local_updates.push_back({current_index, new_intensity, false});
            }
        }
    }
    
    // Merge local updates into the global maps.
    for (const auto& thread_updates : all_local_updates)
    {
        for (const auto& update : thread_updates)
        {
            if (update.is_new)
            {
                fire_map[update.index] = update.value;
                next_front[update.index] = update.value;
            }
            else
            {
                fire_map[update.index] = update.value;
                if (update.value == 0)
                    next_front.erase(update.index);
                else
                    next_front[update.index] = update.value;
            }
        }
    }
    
    fire_front = next_front;
    
    // Create a vector with the indices for vegetation update.
    std::vector<std::size_t> veg_indices;
    veg_indices.reserve(fire_front.size());
    for (const auto &f : fire_front)
        veg_indices.push_back(f.first);
    
    #pragma omp parallel for schedule(dynamic, 64)
    for (std::size_t i = 0; i < veg_indices.size(); i++)
    {
        std::size_t index = veg_indices[i];
        if (vegetation_map[index] > 0)
            vegetation_map[index] -= 1;
    }
    
    time_step += 1;
    return !fire_front.empty();
}


std::size_t Model::get_index_from_coord(Coordinates t_lexico_indices) const
{
    return t_lexico_indices.row * this->get_geometry() + t_lexico_indices.column;
}

struct Model::Coordinates Model::get_coord_from_index(std::size_t t_global_index) const
{
    Coordinates ind_coords;
    ind_coords.row = t_global_index / this->get_geometry();
    ind_coords.column = t_global_index % this->get_geometry();
    return ind_coords;
}
