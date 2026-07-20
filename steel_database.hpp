#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <unordered_map>
#include <stdexcept>

// Safety function to remove invisible junk characters (like Excel's \r)
static inline void trim(std::string &s) {
    size_t start = s.find_first_not_of(" \t\r\n\xEF\xBB\xBF");
    if (start == std::string::npos) {
        s.clear();
        return;
    }
    s.erase(0, start);
    s.erase(s.find_last_not_of(" \t\r\n") + 1);
}

struct SteelProfile {
    std::string name;
    double weight_per_meter;
};

class SteelDatabase {
private:
    std::unordered_map<std::string, SteelProfile> database;

public:
    void loadProfileFromCSV(const std::string& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            std::cerr << "CRITICAL: Could not open " << filepath << "\n";
            return;
        }

        std::string line;
        bool is_header = true;
        
        while (std::getline(file, line)) {
            if (is_header) { is_header = false; continue; } 
            
            std::stringstream ss(line);
            std::string name, weight_str;

            // NEW CSV LAYOUT: Col 1 = Name, Col 2 = Weight
            if (std::getline(ss, name, ',') && std::getline(ss, weight_str, ',')) {
                trim(name);
                trim(weight_str);
                
                try {
                    double weight = std::stod(weight_str);
                    database[name] = {name, weight};
                } catch (...) {
                    // Ignore broken lines silently
                }
            }
        }
    }

    double get_weight(const std::string& profile_name) const {
        std::string search_name = profile_name;
        trim(search_name); // Clean the search term just in case

        auto it = database.find(search_name);
        if (it != database.end()) {
            return it->second.weight_per_meter;
        }
        
        // If it fails, print to terminal and return 0 so the UI doesn't crash
        std::cerr << "Profile not found in C++ Database: [" << search_name << "]\n";
        return 0.0; 
    }
};