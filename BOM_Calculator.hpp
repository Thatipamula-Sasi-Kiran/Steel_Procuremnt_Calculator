#pragma once
#include <iostream>
#include <cmath>
#include <string>
#include "steel_database.hpp"

struct OrderItems {
    std::string profile_name;
    double Weight;
};

struct ProcessedItems {
    std::string profile_name;
    double base_weight_kg;
    double commercial_weight_kg;
    int standard_bars_to_order;
};

class BOMCalculator {
    private:
        const SteelDatabase& db; // Reference to the SteelDatabase instance (&)

        const double standard_bar_length_m;

    public:
        BOMCalculator(const SteelDatabase& database, double standard_length = 12.0) : db(database), standard_bar_length_m(standard_length) {}
};