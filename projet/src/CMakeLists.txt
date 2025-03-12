cmake_minimum_required(VERSION 3.10)
project(SimulationProject CXX)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenMP REQUIRED)
find_package(benchmark REQUIRED)

set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -fbounds-check -pedantic -D_GLIBCXX_DEBUG")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -Wall")

add_executable(measures.exe measures.cpp display.cpp model.cpp)

target_compile_options(measures.exe PRIVATE 
    $<$<CONFIG:Debug>:${CMAKE_CXX_FLAGS_DEBUG}>
    $<$<CONFIG:Release>:${CMAKE_CXX_FLAGS_RELEASE}>
)

target_link_libraries(measures.exe PRIVATE pthread SDL2 OpenMP::OpenMP_CXX)


add_executable(simulation.exe simulation.cpp display.cpp model.cpp)

target_compile_options(simulation.exe PRIVATE 
    $<$<CONFIG:Debug>:${CMAKE_CXX_FLAGS_DEBUG}>
    $<$<CONFIG:Release>:${CMAKE_CXX_FLAGS_RELEASE}>
)

target_link_libraries(simulation.exe PRIVATE pthread SDL2 OpenMP::OpenMP_CXX)