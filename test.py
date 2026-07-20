import bom_core

def main():
    print("--- Python to C++ Bridge Test ---")
    
    # 1. Using YOUR database and YOUR load function
    db = bom_core.SteelDatabase()
    db.loadProfileFromCSV("Indian_Structural_Steel_Database.csv")
    
    # 2. Using YOUR calculator
    calc = bom_core.BOMCalculator(db, 12.0)
    
    # 3. Using YOUR order struct
    order = bom_core.OrderItems("ISMB 200", 10, 5.0)
    
    result = calc.calculate_item(order)
    
    print("\n--- RESULTS FROM C++ ---")
    print(f"Profile: {result.profile_name}")
    print(f"Base Weight: {result.base_weight_kg:.2f} kg")
    print(f"Commercial Weight: {result.commercial_weight_kg:.2f} kg")
    print(f"Standard Bars to Order: {result.standard_bars_to_order}")

if __name__ == "__main__":
    main()