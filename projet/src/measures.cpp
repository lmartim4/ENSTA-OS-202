#include <iostream>
#include <chrono>
#include "model.hpp"
#include <array>

int main(int argc, char* argv[]) {
    // Define simulation parameters.
    double length = 1.0;
    unsigned discretization = 300;
    std::array<double, 2> wind = {0.0, 0.0};
    Model::Coordinates start{10, 10};

    // Create an instance of your simulation model.
    Model simu(length, discretization, wind, start);

    // Variable to count update steps.
    size_t step = 0;

    // Profile each call to update() until it returns false.
    while (true) {
        auto start_time = std::chrono::high_resolution_clock::now();

        bool stillUpdating = simu.update();

        auto end_time = std::chrono::high_resolution_clock::now();
        auto update_duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

        std::cout << "Step " << step 
                  << ": update() took " << update_duration 
                  << " microseconds." << std::endl;

        ++step;
        if (!stillUpdating)
            break;
    }

    return 0;
}
