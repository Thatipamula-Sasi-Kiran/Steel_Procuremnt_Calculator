import customtkinter as ctk
import tkinter.messagebox as tkmb
import csv
import bom_core

# 1. Initialize the C++ Backend Engine
db = bom_core.SteelDatabase()
db.loadProfileFromCSV("Indian_Structural_Steel_Database.csv")
calculator = bom_core.BOMCalculator(db, 12.0)

# 2. Helper to load profile names from the CSV for the dropdown menu
def get_profile_names(filename):
    names = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader) # Skip the header row
            for row in reader:
                if len(row) >= 3:
                    names.append(row[1].strip()) # Profile Name is the second column
    except FileNotFoundError:
        names = ["ISMB 200", "ISMC 150"] # Fallback if CSV is missing
    return names

# 3. Setup the CustomTkinter Window
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

app = ctk.CTk()
app.geometry("500x550")
app.title("Steel Procurement BOM Calculator")
app.resizable(False, False)

# Title Label
title_label = ctk.CTkLabel(app, text="Steel BOM Calculator", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=(20, 5))

subtitle_label = ctk.CTkLabel(app, text="Powered by C++ Core Engine", font=ctk.CTkFont(size=12), text_color="gray")
subtitle_label.pack(pady=(0, 20))

# 4. Input Frame
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Profile Dropdown
profile_label = ctk.CTkLabel(input_frame, text="Select Profile:")
profile_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
profile_names = get_profile_names("Indian_Structural_Steel_Database.csv")
profile_var = ctk.StringVar(value=profile_names[0] if profile_names else "")
profile_dropdown = ctk.CTkComboBox(input_frame, variable=profile_var, values=profile_names, width=200)
profile_dropdown.grid(row=0, column=1, padx=20, pady=10)

# Quantity Input
qty_label = ctk.CTkLabel(input_frame, text="Quantity (pieces):")
qty_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
qty_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. 10", width=200)
qty_entry.grid(row=1, column=1, padx=20, pady=10)

# Length Input
length_label = ctk.CTkLabel(input_frame, text="Length per piece (m):")
length_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
length_entry = ctk.CTkEntry(input_frame, placeholder_text="e.g. 5.0", width=200)
length_entry.grid(row=2, column=1, padx=20, pady=10)

# 5. Results Frame
result_frame = ctk.CTkFrame(app, fg_color="#2b2b2b")
result_frame.pack(pady=10, padx=20, fill="both", expand=True)

res_base_label = ctk.CTkLabel(result_frame, text="Base Weight: --", font=ctk.CTkFont(size=14))
res_base_label.pack(pady=(15, 5))

res_bars_label = ctk.CTkLabel(result_frame, text="Standard Bars to Order: --", font=ctk.CTkFont(size=14))
res_bars_label.pack(pady=5)

res_billed_label = ctk.CTkLabel(result_frame, text="Billed Weight: --", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3a7ebf")
res_billed_label.pack(pady=(5, 5))

res_scrap_label = ctk.CTkLabel(result_frame, text="Scrap (Wastage): --", font=ctk.CTkFont(size=14), text_color="#d9534f")
res_scrap_label.pack(pady=(5, 15))

# 6. Calculation Function (The Bridge in Action)
def calculate_bom():
    try:
        profile = profile_var.get()
        qty = int(qty_entry.get())
        length = float(length_entry.get())
        
        # Call the C++ Engine!
        order = bom_core.OrderItems(profile, qty, length)
        result = calculator.calculate_item(order)
        
        # Update the UI with the fast C++ results
        res_base_label.configure(text=f"Base Weight: {result.base_weight_kg:.2f} kg")
        res_bars_label.configure(text=f"Standard Bars to Order: {result.standard_bars_to_order}")
        res_billed_label.configure(text=f"Billed Weight: {result.commercial_weight_kg:.2f} kg")
        
        # Calculate scrap
        scrap = result.commercial_weight_kg - result.base_weight_kg
        res_scrap_label.configure(text=f"Scrap (Wastage): {scrap:.2f} kg")
        
    except ValueError:
        tkmb.showerror("Input Error", "Please enter valid numbers for Quantity and Length.")
    except Exception as e:
        tkmb.showerror("Calculation Error", f"An error occurred: {str(e)}")

# Calculate Button
calc_button = ctk.CTkButton(app, text="Calculate BOM", command=calculate_bom, height=40, font=ctk.CTkFont(weight="bold"))
calc_button.pack(pady=10)

# Run the app
if __name__ == "__main__":
    app.mainloop()