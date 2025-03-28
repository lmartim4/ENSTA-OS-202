#include <cassert>
#include <stdexcept>
#include <string> 
#include "display.hpp"

using namespace std::string_literals;

std::shared_ptr<Displayer> Displayer::unique_instance{nullptr};

Displayer::Displayer( std::uint32_t t_width, std::uint32_t t_height )
{
    if ( SDL_Init( SDL_INIT_EVERYTHING) < 0 )
    {
        std::string err_msg = "Erreur lors de l'initialisation de SDL : "s + std::string(SDL_GetError());
        throw std::runtime_error(err_msg);
    }
    SDL_CreateWindowAndRenderer(t_width, t_height, 0, &pt_window, &pt_renderer);
    if (pt_window == nullptr)
    {
        std::string err_msg = "Erreur lors de la création de la fenêtre : "s + std::string(SDL_GetError() );
        throw std::runtime_error(err_msg);
    }
    if (pt_renderer == nullptr)
    {
        std::string err_msg = "Erreur lors de la création du moteur de rendu : "s + std::string(SDL_GetError() );
        throw std::runtime_error(err_msg);
    }
    pt_surface = SDL_GetWindowSurface( pt_window );
    if (pt_surface == nullptr)
    {
        std::string err_msg = "Erreur lors de la récupération de la surface : "s + std::string(SDL_GetError() );
        throw std::runtime_error(err_msg);
    }
}

Displayer::~Displayer()
{
    SDL_DestroyRenderer(pt_renderer);
    SDL_DestroyWindow( pt_window );
    SDL_Quit();
}
void Displayer::update( std::vector<std::uint8_t> const & vegetation_global_map, std::vector<std::uint8_t> const & fire_global_map )
{
    int w, h;
    SDL_GetWindowSize(pt_window, &w, &h );
    SDL_SetRenderDrawColor(pt_renderer, 0,0,0, 255);
    SDL_RenderClear(pt_renderer);
    for (int i = 0; i < h; ++i )
      for (int j =  0; j < w; ++j )
      {
        SDL_SetRenderDrawColor(pt_renderer, fire_global_map[j + w*i], vegetation_global_map[j + w*i], 0, 255);
        SDL_RenderDrawPoint(pt_renderer, j, h-i-1); 
      }
    SDL_RenderPresent(pt_renderer);
}

std::shared_ptr<Displayer> Displayer::init_instance( std::uint32_t t_width, std::uint32_t t_height )
{
    assert( ( "L'initialisation de l'instance ne doit etre appele qu'une seule fois !" && (unique_instance == nullptr) ) );
    unique_instance = std::make_shared<Displayer>(t_width, t_height);
    return unique_instance;
}
std::shared_ptr<Displayer> Displayer::instance()
{
    assert( ( "Il faut initialiser l'instance avant tout !" && (unique_instance != nullptr) ) );
    return unique_instance;
}