#include <chrono>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <string>
#include <omp.h>

class Profiler
{
public:
    Profiler(const std::string &filename, const std::string &header)
    {
        std::filesystem::create_directories("../logs");

        csv_file = std::ofstream("../logs/" + filename, std::ios::out);
        if (!csv_file.is_open())
        {
            std::cerr << "Unable to open CSV file for profiling" << std::endl;
            exit(EXIT_FAILURE);
        }
        csv_file << header;
        int num_threads = omp_get_max_threads();

        csv_file << "OpenMP threads: " << num_threads << "\n";
        csv_file << "step,update_time,display_time,total_time\n";
    }

    void start(const std::string &section)
    {
        timestamps[section] = std::chrono::high_resolution_clock::now();
    }

    void stop(const std::string &section)
    {
        auto end_time = std::chrono::high_resolution_clock::now();
        if (timestamps.find(section) != timestamps.end())
        {
            durations[section] = std::chrono::duration_cast<std::chrono::microseconds>(end_time - timestamps[section]).count();
        }
    }

    void log(int step)
    {
        csv_file << step << ","
                 << durations["update"] << ","
                 << durations["display"] << ","
                 << durations["total"] << "\n";
    }

    ~Profiler()
    {
        if (csv_file.is_open())
        {
            csv_file.close();
        }
    }

private:
    std::unordered_map<std::string, std::chrono::high_resolution_clock::time_point> timestamps;
    std::unordered_map<std::string, long long> durations;
    std::ofstream csv_file;
};
