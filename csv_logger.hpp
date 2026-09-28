#ifndef CSV_LOGGER_HPP
#define CSV_LOGGER_HPP

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <filesystem>
#include <mutex>
#include <initializer_list>

class CSVLogger {
private:
    std::string filename_;
    std::mutex mutex_;

    // Helper to format a single value into a CSV-compliant string
    template <typename T>
    static std::string formatValue(const T& val) {
        std::ostringstream oss;
        oss << val;
        return oss.str();
    }

    // Overload specifically for strings to escape quotes/commas safely
    static std::string formatValue(const std::string& val) {
        return "\"" + val + "\"";
    }

    static std::string formatValue(const char* val) {
        return "\"" + std::string(val) + "\"";
    }

public:
    explicit CSVLogger(std::string filename) : filename_(std::move(filename)) {}

    // Option A: Set column headers once
    void setHeaders(const std::vector<std::string>& headers) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!std::filesystem::exists(filename_)) {
            std::ofstream file(filename_, std::ios::app);
            for (size_t i = 0; i < headers.size(); ++i) {
                file << headers[i] << (i + 1 < headers.size() ? "," : "\n");
            }
        }
    }

    // Option B: Log arbitrary parameter packs (Variadic Template)
    template <typename... Args>
    bool log(const Args&... args) {
        std::lock_guard<std::mutex> lock(mutex_);
        std::ofstream file(filename_, std::ios::app);

        if (!file.is_open()) {
            std::cerr << "[CSVLogger Error] Could not open file: " << filename_ << std::endl;
            return false;
        }

        // Convert parameter pack into a vector of strings using fold expression / initializer list
        std::vector<std::string> row = { formatValue(args)... };

        for (size_t i = 0; i < row.size(); ++i) {
            file << row[i] << (i + 1 < row.size() ? "," : "\n");
        }

        return true;
    }
};

inline CSVLogger logger("parameters.csv");

#endif // CSV_LOGGER_HPP