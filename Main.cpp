#include <iostream>
#include <fstream>
#include <string>
#include <sstream> // For 'funneling' the data into a string stream

int main(){
    std::ifstream myFile("Indian_Structural_Steel_Database.csv"); //Input File Stream

    if (myFile.is_open()) {
        std::string line;
        std::getline(myFile, line); // Read the first line (header) and ignore it
        double weightValue = 0.0;

        while (std::getline(myFile, line)) {
            std::stringstream ss(line);
            std::string category, name, weight;

            if (std::getline(ss, category, ',')) {
                if (std::getline(ss, name, ',')){
                    if(std::getline(ss, weight, ',')){
                        std::cout << "Category: " << category << " | Profile: " << name << " | Weight: " << weight << std::endl; // Print Each line in a organized format
                        weightValue += std::stod(weight); // Convert weight string to double and add to weightValue
                    }
                }
            }
            //std::cout << line << std::endl; // Print each line
        }
        std::cout << "Total Weight: " << weightValue << std::endl;

        myFile.close(); // Close the file
    } else {
        std::cout << "Could not open the file" << std::endl;
    }

    return 0;
}