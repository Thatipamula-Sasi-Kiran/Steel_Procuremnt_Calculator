import customtkinter as ctk
import tkinter.messagebox as tkmb
import csv
import bom_core
import os
import sys
import math

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CSV_PATH = resource_path("Indian_Structural_Steel_Database.csv")

db = bom_core.SteelDatabase()
if os.path.exists(CSV_PATH):
    db.loadProfileFromCSV(CSV_PATH)
else:
    print(f"CRITICAL ERROR: Database file not found at {CSV_PATH}")

calculator = bom_core.BOMCalculator(db, 12.0)

profile_details = {}

def load_profiles():
    categories = {}
    if not os.path.exists(CSV_PATH):
        return {"Default": ["ISMB 100"]}
        
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                if len(row) >= 5:
                    name = row[0].strip()
                    cat = row[4].strip()
                    
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(name)
                    
                    profile_details[name] = {
                        "depth": row[2].strip(),
                        "width": row[3].strip(),
                        "cat": cat
                    }
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {"Default": ["ISMB 100"]}
        
    return categories

PROFILE_DATA = load_profiles()
CATEGORY_NAMES = list(PROFILE_DATA.keys())

class ReportWindow(ctk.CTkToplevel):
    def __init__(self, parent, results, grand_total_wt, grand_total_scrap):
        super().__init__(parent)
        self.title("Bill of Materials - Report")
        self.geometry("1150x500") 
        
        title = ctk.CTkLabel(self, text="Project Bill of Materials", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(15, 10))
        
        self.table_frame = ctk.CTkScrollableFrame(self, width=1100, height=300)
        self.table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Updated Header Order: Bars/Sheets moved to the end
        headers = ["S.No", "Item Profile", "Dimensions", "Qty", "Scrap %", "Scrap", "Billed Wt", "Tonnage (MT)", "Bars/Sheets"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=10, pady=5, sticky="w")
            
        separator = ctk.CTkFrame(self.table_frame, height=2, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=len(headers), sticky="ew", pady=5)
        
        for row_idx, res in enumerate(results, start=2):
            ctk.CTkLabel(self.table_frame, text=str(res['sno'])).grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=res['profile']).grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            
            # Show input dimensions neatly
            dim_text = f"{res['length']:.0f} mm" if not res['is_plate'] else f"{res['length']}' x {res['width']}' ft"
            ctk.CTkLabel(self.table_frame, text=dim_text).grid(row=row_idx, column=2, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=str(res['qty'])).grid(row=row_idx, column=3, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=f"{res['scrap_pct']}%", text_color="#f0ad4e").grid(row=row_idx, column=4, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{res['scrap_wt']:.2f} kg", text_color="#f0ad4e", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=5, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=f"{res['billed_wt']:.2f} kg", text_color="#3a7ebf", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=6, padx=10, pady=5, sticky="w")
            
            # Tonnage rounded up elegantly to 3 decimals
            ctk.CTkLabel(self.table_frame, text=f"{res['tonnage']:.3f} MT", text_color="#5cb85c", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=7, padx=10, pady=5, sticky="w")
            
            # Moved Bars/Sheets to the final column
            ctk.CTkLabel(self.table_frame, text=str(res['bars'])).grid(row=row_idx, column=8, padx=10, pady=5, sticky="w")

        total_frame = ctk.CTkFrame(self)
        total_frame.pack(fill="x", padx=20, pady=15)
        
        grand_tonnage = math.ceil((grand_total_wt / 1000.0) * 1000.0) / 1000.0
        
        scrap_lbl = ctk.CTkLabel(total_frame, text=f"TOTAL SCRAP: {grand_total_scrap:.2f} kg", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f0ad4e")
        scrap_lbl.pack(side="left", padx=20, pady=10)

        grand_lbl = ctk.CTkLabel(total_frame, text=f"GRAND TOTAL: {grand_total_wt:.2f} kg  ({grand_tonnage:.3f} MT)", font=ctk.CTkFont(size=18, weight="bold"), text_color="#28a745")
        grand_lbl.pack(side="right", padx=20, pady=10)

class SteelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Steel BOM Calculator")
        self.geometry("950x600") 
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.rows = [] 
        
        self.header = ctk.CTkLabel(self, text="Steel Procurement List", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 5))
        
        self.sub = ctk.CTkLabel(self, text="Linear = mm | Plates = feet", text_color="gray")
        self.sub.pack(pady=(0, 15))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=15)
        
        self.add_btn = ctk.CTkButton(self.btn_frame, text="+ Add Item", command=self.add_item_row, fg_color="#444444", hover_color="#555555")
        self.add_btn.pack(side="left", padx=10)
        
        self.calc_btn = ctk.CTkButton(self.btn_frame, text="Generate BOM Receipt", command=self.calculate_all, height=40, font=ctk.CTkFont(weight="bold"))
        self.calc_btn.pack(side="right", padx=10)
        
        self.add_item_row()

    def add_item_row(self):
        row_data = {}
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", pady=5)
        
        sno_lbl = ctk.CTkLabel(row_frame, text=f"{len(self.rows) + 1}.")
        sno_lbl.pack(side="left", padx=10)
        
        cat_var = ctk.StringVar(value=CATEGORY_NAMES[0] if CATEGORY_NAMES else "")
        cat_dropdown = ctk.CTkComboBox(row_frame, variable=cat_var, values=CATEGORY_NAMES, width=120)
        cat_dropdown.pack(side="left", padx=10)
        
        current_profiles = PROFILE_DATA.get(cat_var.get(), ["--"])
        profile_var = ctk.StringVar(value=current_profiles[0])
        profile_dropdown = ctk.CTkComboBox(row_frame, variable=profile_var, values=current_profiles, width=160)
        profile_dropdown.pack(side="left", padx=10)
        
        qty_entry = ctk.CTkEntry(row_frame, placeholder_text="Qty", width=50)
        qty_entry.pack(side="left", padx=10)
        
        len_entry = ctk.CTkEntry(row_frame, placeholder_text="Len (mm)", width=70)
        len_entry.pack(side="left", padx=10)

        # Initialize without placeholder to avoid render bugs
        wid_entry = ctk.CTkEntry(row_frame, width=70)
        wid_entry.pack(side="left", padx=10)
        
        scrap_entry = ctk.CTkEntry(row_frame, placeholder_text="Scrap %", width=65)
        scrap_entry.pack(side="left", padx=10)
        
        # DYNAMIC UI LOGIC
        def update_ui_for_category(*args):
            choice = cat_var.get()
            new_profiles = PROFILE_DATA.get(choice, ["--"])
            profile_dropdown.configure(values=new_profiles)
            profile_var.set(new_profiles[0])
            
            if choice == "Plate" or choice == "Grating":
                len_entry.configure(placeholder_text="Len (ft)")
                wid_entry.configure(state="normal")
                wid_entry.configure(placeholder_text="Wid (ft)")
            else:
                len_entry.configure(placeholder_text="Len (mm)")
                # Temporarily enable to safely clear and update placeholder
                wid_entry.configure(state="normal") 
                wid_entry.delete(0, 'end')
                wid_entry.configure(placeholder_text="--")
                wid_entry.configure(state="disabled")
                
        cat_dropdown.configure(command=update_ui_for_category)
        update_ui_for_category() # Run once to set initial state
        
        def remove_self():
            row_frame.destroy()
            self.rows.remove(row_data)
            self.update_serial_numbers()
            
        remove_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#d9534f", hover_color="#c9302c", command=remove_self)
        remove_btn.pack(side="right", padx=10)
        
        row_data = {
            "frame": row_frame,
            "sno_lbl": sno_lbl,
            "profile": profile_var,
            "qty": qty_entry,
            "length": len_entry,
            "width": wid_entry,
            "scrap": scrap_entry
        }
        self.rows.append(row_data)

    def update_serial_numbers(self):
        for idx, row in enumerate(self.rows):
            row["sno_lbl"].configure(text=f"{idx + 1}.")

    def calculate_all(self):
        if not self.rows:
            tkmb.showwarning("Empty List", "Please add at least one item.")
            return
            
        results = []
        grand_total_wt = 0.0
        grand_total_scrap = 0.0 
        
        for idx, row in enumerate(self.rows):
            prof = row["profile"].get()
            qty_str = row["qty"].get()
            len_str = row["length"].get()
            wid_str = row["width"].get()
            scrap_str = row["scrap"].get()
            
            is_plate = profile_details.get(prof, {}).get("cat") in ["Plate", "Grating"]
            
            if not qty_str or not len_str:
                tkmb.showerror("Missing Data", f"Item {idx+1} is missing Quantity or Length.")
                return
            if is_plate and not wid_str:
                tkmb.showerror("Missing Data", f"Item {idx+1} is a Plate and requires a Width.")
                return
                
            try:
                qty = int(qty_str)
                length = float(len_str)
                width = float(wid_str) if is_plate else 0.0
                scrap_pct = float(scrap_str) if scrap_str else 0.0
            except ValueError:
                tkmb.showerror("Invalid Input", f"Item {idx+1} has invalid numbers.")
                return
                
            try:
                # Send all 4 variables to the new C++ Engine!
                order = bom_core.OrderItems(prof, qty, length, width)
                res = calculator.calculate_item(order)
                
                scrap_wt = res.commercial_weight_kg * (scrap_pct / 100.0)
                tonnage = math.ceil((res.commercial_weight_kg / 1000.0) * 1000) / 1000.0
                
                results.append({
                    "sno": idx + 1,
                    "profile": prof,
                    "length": length,
                    "width": width,
                    "is_plate": is_plate,
                    "qty": qty,
                    "bars": res.standard_bars_to_order,
                    "scrap_pct": scrap_pct,
                    "scrap_wt": scrap_wt,
                    "billed_wt": res.commercial_weight_kg,
                    "tonnage": tonnage
                })
                
                grand_total_wt += res.commercial_weight_kg
                grand_total_scrap += scrap_wt
                
            except Exception as e:
                tkmb.showerror("Engine Error", f"Failed calculating item {idx+1}: {e}")
                return
                
        ReportWindow(self, results, grand_total_wt, grand_total_scrap)

if __name__ == "__main__":
    app = SteelApp()
    app.mainloop()