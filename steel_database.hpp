#pragma once
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <unordered_map>

struct SteelProfile {
    std::string category;
    std::string name;
    double weight;
};

class SteelDatabase {
    private:
        std::unordered_map<std::string, SteelProfile> profiles;
    
    public:
        void loadProfileFromCSV(const std::string& filepath) {
            std::ifstream myFile(filepath); // Input File Stream

            if (myFile.is_open()) {
                std::string line;
                std::getline(myFile, line); // Read the first line (header) and ignore it

                while (std::getline(myFile, line)) {
                    std::stringstream ss(line);
                    std::string category, name, weight;

                    if (std::getline(ss, category, ',')) {
                        if (std::getline(ss, name, ',')) {
                            if (std::getline(ss, weight, ',')) {
                                SteelProfile profile{category, name, std::stod(weight)};
                                profiles[name] = profile; // Store the profile in the map with name as key
                            }
                        }
                    }
                }
                myFile.close(); // Close the file
            } else {
                std::cout << "Could not open the file" << std::endl;
            }
        }

        void displayProfiles() const {
            for (const auto& pair : profiles) {
                const SteelProfile& profile = pair.second;
                std::cout << "Category: " << profile.category << " | Profile: " << profile.name << " | Weight: " << profile.weight << std::endl;
            }
        }

        double get_weight(std::string profile_name) const {
            auto it = profiles.find(profile_name);
            if (it != profiles.end()) {
                return it->second.weight;
            } else {
                std::cout << "Profile not found" << std::endl;
                return 0.0; // Add this line!
            }
        }
};