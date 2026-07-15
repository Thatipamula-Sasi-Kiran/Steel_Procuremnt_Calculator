#include <iostream>
#include <fstream>
#include <string>
#include "steel_database.hpp"

int main(){
    SteelDatabase steelDB;

    steelDB.loadProfileFromCSV("Indian_Structural_Steel_Database.csv");

    steelDB.displayProfiles();
    return 0;
}