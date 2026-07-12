#include <iostream>
#include <fstream>
#include <string>

int main(){
    std::ifstream myFile("Indian_Structural_Steel_Database.csv"); //Input File Stream

    if (myFile.is_open()) {
        std::string line;

        while (std::getline(myFile, line)) {
            std::cout << line << std::endl; // Print each line
        }

        myFile.close(); // Close the file
    } else {
        std::cout << "Could not open the file" << std::endl;
    }

    return 0;
}