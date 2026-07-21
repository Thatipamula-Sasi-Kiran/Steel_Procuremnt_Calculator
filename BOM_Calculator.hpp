#pragma once
#include <string>
#include <vector>
#include <cmath>
#include <unordered_map>
#include <stdexcept>
#include "steel_database.hpp"

// TIER 0: The Input Struct
struct OrderItems {
    std::string drawing_name;
    std::string profile_name;
    int quantity;
    double length_mm;
    double width_mm; 
    
    OrderItems() : quantity(0), length_mm(0.0), width_mm(0.0) {}
    OrderItems(std::string d, std::string p, int q, double l, double w) 
        : drawing_name(d), profile_name(p), quantity(q), length_mm(l), width_mm(w) {}
};

// TIER 1: The Blueprint Math (Per Drawing)
struct DrawingItemResult {
    std::string drawing_name;
    std::string profile_name;
    int quantity;
    double length_mm;
    double width_mm;
    double exact_weight_kg;
    double exact_total_length_or_area; // Meters (m) for linear, Sq.Meters (m2) for plates
    bool is_plate;
};

// TIER 2: The Procurement Math (Project Summary)
struct SummaryItemResult {
    std::string profile_name;
    double grand_total_length_or_area;
    double unit_weight; 
    int standard_bars_to_order;
    double commercial_weight_kg;
    double tonnage_mt;
    bool is_plate;
    std::string recommended_plate_size; // Holds the AI recommendation
};

// The Master Container sent back to Python
struct ProjectResult {
    std::vector<DrawingItemResult> drawing_items;
    std::vector<SummaryItemResult> summary_items;
    double grand_total_tonnage;
};

class BOMCalculator {
private:
    const SteelDatabase& db;
    double standard_bar_length_m; 

public:
    BOMCalculator(const SteelDatabase& database, double standard_length = 12.0) 
        : db(database), standard_bar_length_m(standard_length) {}

    ProjectResult calculate_project(const std::vector<OrderItems>& project_items) {
        ProjectResult final_result;
        final_result.grand_total_tonnage = 0.0;
        
        // This map aggregates area/length by exact profile name
        std::unordered_map<std::string, double> aggregated_totals;

        // --- PASS 1: Drawing-Level Blueprint Math ---
        for (const auto& item : project_items) {
            DrawingItemResult d_res;
            d_res.drawing_name = item.drawing_name;
            d_res.profile_name = item.profile_name;
            d_res.quantity = item.quantity;
            d_res.length_mm = item.length_mm;
            d_res.width_mm = item.width_mm;
            
            SteelProfile prof = db.get_profile(item.profile_name);
            d_res.is_plate = (prof.category == "Plate" || prof.category == "Grating");

            if (d_res.is_plate) {
                // Exact Area in square meters
                double area_m2 = (item.length_mm / 1000.0) * (item.width_mm / 1000.0) * item.quantity;
                d_res.exact_total_length_or_area = area_m2;
                d_res.exact_weight_kg = area_m2 * prof.weight; // prof.weight is kg/m2
                
                aggregated_totals[item.profile_name] += area_m2;
            } else {
                // Exact Length in meters
                double length_m = (item.length_mm / 1000.0) * item.quantity;
                d_res.exact_total_length_or_area = length_m;
                d_res.exact_weight_kg = length_m * prof.weight; // prof.weight is kg/m
                
                aggregated_totals[item.profile_name] += length_m;
            }
            
            final_result.drawing_items.push_back(d_res);
        }

        // --- PASS 2: Project-Level Procurement Math ---
        for (const auto& [profile, total_amount] : aggregated_totals) {
            SummaryItemResult s_res;
            s_res.profile_name = profile;
            s_res.grand_total_length_or_area = total_amount;
            
            SteelProfile prof = db.get_profile(profile);
            s_res.unit_weight = prof.weight;
            s_res.is_plate = (prof.category == "Plate" || prof.category == "Grating");
            
            if (s_res.is_plate) {
                // DUAL-PLATE AI: Test both standard sizes
                double area_sheet_1 = 1.25 * 2.50; // 1250 x 2500 mm
                double area_sheet_2 = 1.50 * 6.30; // 1500 x 6300 mm
                
                int sheets_needed_1 = std::ceil(total_amount / area_sheet_1);
                double billed_wt_1 = sheets_needed_1 * area_sheet_1 * prof.weight;
                
                int sheets_needed_2 = std::ceil(total_amount / area_sheet_2);
                double billed_wt_2 = sheets_needed_2 * area_sheet_2 * prof.weight;
                
                // Pick the most efficient size (lowest billed weight means lowest scrap)
                if (billed_wt_1 <= billed_wt_2) {
                    s_res.recommended_plate_size = "1250 x 2500 mm";
                    s_res.standard_bars_to_order = sheets_needed_1;
                    s_res.commercial_weight_kg = billed_wt_1;
                } else {
                    s_res.recommended_plate_size = "1500 x 6300 mm";
                    s_res.standard_bars_to_order = sheets_needed_2;
                    s_res.commercial_weight_kg = billed_wt_2;
                }
            } else {
                // Linear Math
                s_res.recommended_plate_size = "-";
                s_res.standard_bars_to_order = std::ceil(total_amount / standard_bar_length_m);
                s_res.commercial_weight_kg = s_res.standard_bars_to_order * standard_bar_length_m * prof.weight;
            }
            
            s_res.tonnage_mt = std::ceil((s_res.commercial_weight_kg / 1000.0) * 1000) / 1000.0;
            final_result.grand_total_tonnage += s_res.tonnage_mt;
            
            final_result.summary_items.push_back(s_res);
        }

        return final_result;
    }
};