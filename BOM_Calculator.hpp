#pragma once
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include "steel_database.hpp"

// Updated to accept Width!
struct OrderItems {
    std::string profile_name;
    int quantity;
    double length; // mm for linear, feet for plate
    double width;  // feet (only used for plates)
    
    // Constructors for Python Bridge
    OrderItems() : quantity(0), length(0.0), width(0.0) {}
    OrderItems(std::string name, int q, double l, double w) 
        : profile_name(name), quantity(q), length(l), width(w) {}
};

struct ProcessedItems {
    std::string profile_name;
    double base_weight_kg;
    double commercial_weight_kg;
    int standard_bars_to_order; // Used for "Sheets" or "Bars"
};

class BOMCalculator {
private:
    const SteelDatabase& db;
    double standard_bar_length; 

public:
    BOMCalculator(const SteelDatabase& database, double standard_length = 12.0) 
        : db(database), standard_bar_length(standard_length) {}

    ProcessedItems calculate_item(const OrderItems& order) {
        ProcessedItems result;
        result.profile_name = order.profile_name;

        SteelProfile prof = db.get_profile(order.profile_name);
        
        if (prof.category == "Plate" || prof.category == "Grating") {
            // --- 2D SHEET GRID FITTING MATH ---
            double sheet_len_ft = 8.0;
            double sheet_wid_ft = 4.0;
            
            // Test 1: Fit normally
            int fit_l = std::floor(sheet_len_ft / order.length);
            int fit_w = std::floor(sheet_wid_ft / order.width);
            int pieces_normal = fit_l * fit_w;
            
            // Test 2: Fit rotated 90 degrees
            int fit_l_rot = std::floor(sheet_len_ft / order.width);
            int fit_w_rot = std::floor(sheet_wid_ft / order.length);
            int pieces_rotated = fit_l_rot * fit_w_rot;
            
            // Algorithm automatically picks the best orientation to minimize scrap!
            int best_fit_per_sheet = std::max(pieces_normal, pieces_rotated);
            
            if (best_fit_per_sheet == 0) {
                throw std::runtime_error("Piece is larger than a standard 8x4 sheet!");
            }
            
            result.standard_bars_to_order = std::ceil((double)order.quantity / best_fit_per_sheet);
            
            // 8ft * 4ft = 32 sq ft. (1 sq ft = 0.092903 sq meters)
            double sheet_weight = (32.0 * 0.092903) * prof.weight; 
            
            result.commercial_weight_kg = result.standard_bars_to_order * sheet_weight;
            result.base_weight_kg = order.quantity * (order.length * order.width * 0.092903) * prof.weight;
            
        } else {
            // --- LINEAR MATH ---
            // Convert mm to meters automatically
            double length_m = order.length / 1000.0;
            
            result.base_weight_kg = order.quantity * length_m * prof.weight;
            result.standard_bars_to_order = std::ceil((order.quantity * length_m) / standard_bar_length);
            result.commercial_weight_kg = result.standard_bars_to_order * standard_bar_length * prof.weight;
        }
        
        return result;
    }
};