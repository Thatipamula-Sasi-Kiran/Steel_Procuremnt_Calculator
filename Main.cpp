#include <iostream>
#include <fstream>
#include <string>
#include "steel_database.hpp"
#include "BOM_Calculator.hpp"

int main(){
    try{
        SteelDatabase steelDB;

        steelDB.loadProfileFromCSV("Indian_Structural_Steel_Database.csv");

        BOMCalculator calculator(steelDB, 12.0);

        OrderItems order = {"ISMB 200", 10, 5.0}; // Example order: 10 pieces of ISMB 200, each 6 meters long

        ProcessedItems result = calculator.calculate_item(order);
        
        std::cout << "--- BOM RESULT ---\n";
        std::cout << "Profile: " << result.profile_name << "\n";
        std::cout << "Base Weight: " << result.base_weight_kg << " kg (Exact Math)\n";
        std::cout << "Bars to Order: " << result.standard_bars_to_order << " standard bars\n";
        std::cout << "Commercial Weight: " << result.commercial_weight_kg << " kg (Billed Amount)\n";

    } catch (const std::exception& e) {
        std::cerr << "Fatal Error: " << e.what() << "\n";
    }

    //steelDB.displayProfiles();
    return 0;
}