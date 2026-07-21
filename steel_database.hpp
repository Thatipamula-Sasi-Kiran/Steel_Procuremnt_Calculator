#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <unordered_map>
#include <stdexcept>
#include <vector>

// Helper to remove whitespace from strings
static inline void trim(std::string &s) {
    size_t start = s.find_first_not_of(" \t\r\n\xEF\xBB\xBF");
    if (start == std::string::npos) {
        s.clear();
        return;
    }
    s.erase(0, start);
    s.erase(s.find_last_not_of(" \t\r\n") + 1);
}

// Upgraded to hold Category so the Engine knows if it's a Plate
struct SteelProfile {
    std::string name;
    double weight;
    std::string category;
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
            std::string col;
            std::vector<std::string> cols;
            
            while(std::getline(ss, col, ',')) {
                trim(col);
                cols.push_back(col);
            }

            // Index 0: Name, 1: Weight, 2: Depth, 3: Width, 4: Category
            if (cols.size() >= 5) {
                try {
                    double weight = std::stod(cols[1]);
                    database[cols[0]] = {cols[0], weight, cols[4]};
                } catch (...) {}
            }
        }
    }

    SteelProfile get_profile(const std::string& profile_name) const {
        std::string search_name = profile_name;
        trim(search_name); 

        auto it = database.find(search_name);
        if (it != database.end()) {
            return it->second;
        }
        
        return {"Unknown", 0.0, "Unknown"}; 
    }
    
    // Kept for backward compatibility just in case
    double get_weight(const std::string& profile_name) const {
        return get_profile(profile_name).weight;
    }
};