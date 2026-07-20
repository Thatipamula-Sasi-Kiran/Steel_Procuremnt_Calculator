#pragma once
#include <iostream>
#include <cmath>
#include <string>
#include "steel_database.hpp"

struct OrderItems {
    std::string profile_name;
    int quantity;
    double length_per_item_m;
};

struct ProcessedItems {
    std::string profile_name;
    double base_weight_kg;
    double commercial_weight_kg;
    int standard_bars_to_order;
};

class BOMCalculator {
    private:
        const SteelDatabase& Steeldb; // Reference to the SteelDatabase instance (&)

        const double standard_bar_length_m;

    public:
        BOMCalculator(const SteelDatabase& database, double standard_length = 12.0) : Steeldb(database), standard_bar_length_m(standard_length) {}

        ProcessedItems calculate_item(const OrderItems& order) {
            ProcessedItems result;
            result.profile_name = order.profile_name;

            double weight_per_meter = Steeldb.get_weight(order.profile_name);

            double total_length_m = order.quantity * order.length_per_item_m;

            result.base_weight_kg = weight_per_meter * total_length_m;

            double standard_bars_needed = std::ceil(total_length_m / standard_bar_length_m);

            result.standard_bars_to_order = static_cast<int>(standard_bars_needed);
            result.commercial_weight_kg = result.standard_bars_to_order * standard_bar_length_m * weight_per_meter;

            return result;
        }
};