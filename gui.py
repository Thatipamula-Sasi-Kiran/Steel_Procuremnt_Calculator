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
                    
                    try:
                        weight = float(row[1].strip())
                    except ValueError:
                        weight = 0.0
                        
                    cat = row[4].strip()
                    
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(name)
                    
                    profile_details[name] = {
                        "weight": weight,
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

class MathWindow(ctk.CTkToplevel):
    def __init__(self, parent, res):
        super().__init__(parent)
        self.title(f"Math Audit: {res['profile']}")
        self.geometry("600x580")
        self.attributes("-topmost", True) 
        
        header = ctk.CTkLabel(self, text="⚙️ C++ Engine Audit Trail", font=ctk.CTkFont(size=18, weight="bold"))
        header.pack(pady=(15, 5))
        
        self.container = ctk.CTkScrollableFrame(self, fg_color="#1e1e1e") 
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- TOP TEXT (Parameters ONLY) ---
        top_text = ""
        if res['is_plate']:
            top_text += f"INPUT PARAMETERS:\n"
            top_text += f"-----------------\n"
            top_text += f"Category   : Plate / Sheet\n"
            top_text += f"Profile    : {res['profile']}\n"
            top_text += f"Required   : {res['qty']} pieces\n"
            top_text += f"Dimensions : {res['length']}' x {res['width']}'\n"
        else:
            top_text += f"INPUT PARAMETERS:\n"
            top_text += f"-----------------\n"
            top_text += f"Category   : Linear (Beam/Pipe/Angle/etc)\n"
            top_text += f"Profile    : {res['profile']}\n"
            top_text += f"Required   : {res['qty']} pieces\n"
            top_text += f"Dimensions : {res['length']} mm per piece\n"

        self.top_lbl = ctk.CTkLabel(self.container, text=top_text, justify="left", font=ctk.CTkFont("Consolas", 13))
        self.top_lbl.pack(anchor="w", padx=10, pady=(10, 5))
        
        # --- INTERACTIVE EXPANDER BUTTON ---
        self.is_expanded = False
        self.toggle_btn = ctk.CTkButton(self.container, text="▶ Show Weight Calculation Breakdown", 
                                        fg_color="#333333", hover_color="#444444", anchor="w",
                                        command=self.toggle_breakdown)
        self.toggle_btn.pack(fill="x", padx=10, pady=5)
        
        # --- EXPANDABLE BREAKDOWN FRAME (Chronological Story) ---
        self.breakdown_frame = ctk.CTkFrame(self.container, fg_color="#2a2d2e")
        breakdown_text = ""
        wt = res['unit_wt']
        
        if res['is_plate']:
            area_sqft = res['length'] * res['width']
            area_sqm = area_sqft * 0.092903
            
            breakdown_text += f" STEP 1: EXACT MATERIAL NEED (BASE WEIGHT)\n"
            breakdown_text += f" -----------------------------------------\n"
            breakdown_text += f" Unit Weight  = {wt:.2f} kg/m²\n"
            breakdown_text += f" Piece Area   = {res['length']}' x {res['width']}' = {area_sqft:.2f} sq.ft\n"
            breakdown_text += f" Area in m²   = {area_sqft:.2f} sq.ft * 0.092903 = {area_sqm:.4f} m²\n"
            breakdown_text += f" Base Weight  = {res['qty']} pieces * {area_sqm:.4f} m² * {wt:.2f} kg/m²\n"
            breakdown_text += f"              = {res['base_wt']:.2f} kg\n\n"
            
            breakdown_text += f" STEP 2: COMMERCIAL ORDER (BILLED WEIGHT)\n"
            breakdown_text += f" ----------------------------------------\n"
            breakdown_text += f" Standard Sheet = 8 ft x 4 ft (32 sq.ft = 2.9729 m²)\n"
            breakdown_text += f" Nesting Engine = Fitted {res['qty']} pieces into {res['bars']} standard sheets\n"
            breakdown_text += f" Billed Weight  = {res['bars']} sheets * 2.9729 m² * {wt:.2f} kg/m²\n"
            breakdown_text += f"                = {res['billed_wt']:.2f} kg\n"
        else:
            total_m = (res['length'] / 1000.0) * res['qty']
            comm_m = res['bars'] * 12.0
            
            breakdown_text += f" STEP 1: EXACT MATERIAL NEED (BASE WEIGHT)\n"
            breakdown_text += f" -----------------------------------------\n"
            breakdown_text += f" Unit Weight  = {wt:.2f} kg/m\n"
            breakdown_text += f" Total Length = {res['qty']} pieces * {res['length']:.0f} mm = {total_m:.2f} m\n"
            breakdown_text += f" Base Weight  = {total_m:.2f} m * {wt:.2f} kg/m\n"
            breakdown_text += f"              = {res['base_wt']:.2f} kg\n\n"
            
            breakdown_text += f" STEP 2: COMMERCIAL ORDER (BILLED WEIGHT)\n"
            breakdown_text += f" ----------------------------------------\n"
            breakdown_text += f" Standard Bar  = 12.0 meters\n"
            breakdown_text += f" Bars Required = Ceiling({total_m:.2f} m / 12.0 m) = {res['bars']} bars\n"
            breakdown_text += f" Billed Length = {res['bars']} bars * 12.0 m = {comm_m:.2f} m\n"
            breakdown_text += f" Billed Weight = {comm_m:.2f} m * {wt:.2f} kg/m\n"
            breakdown_text += f"               = {res['billed_wt']:.2f} kg\n"
            
        self.breakdown_lbl = ctk.CTkLabel(self.breakdown_frame, text=breakdown_text, justify="left", 
                                          font=ctk.CTkFont("Consolas", 12), text_color="#a8c7fa")
        self.breakdown_lbl.pack(anchor="w", padx=15, pady=10)
        
        # --- BOTTOM TEXT (Financial) ---
        bottom_text = f"\nFINANCIAL / REPORTING:\n"
        bottom_text += f"----------------------\n"
        bottom_text += f"User Scrap Rate     : {res['scrap_pct']} %\n"
        bottom_text += f"Scrap Subtotal      : {res['scrap_wt']:.2f} kg\n"
        bottom_text += f"Final Tonnage (MT)  : {res['tonnage']:.3f} MT\n"

        self.bottom_lbl = ctk.CTkLabel(self.container, text=bottom_text, justify="left", font=ctk.CTkFont("Consolas", 13))
        self.bottom_lbl.pack(anchor="w", padx=10, pady=(0, 10))
        
        close_btn = ctk.CTkButton(self, text="Close Window", command=self.destroy)
        close_btn.pack(pady=(0, 15))

    def toggle_breakdown(self):
        if self.is_expanded:
            self.breakdown_frame.pack_forget()
            self.bottom_lbl.pack_forget()
            self.bottom_lbl.pack(anchor="w", padx=10, pady=(0, 10))
            self.toggle_btn.configure(text="▶ Show Weight Calculation Breakdown")
            self.is_expanded = False
        else:
            self.bottom_lbl.pack_forget()
            self.breakdown_frame.pack(fill="x", padx=10, pady=5)
            self.bottom_lbl.pack(anchor="w", padx=10, pady=(0, 10))
            self.toggle_btn.configure(text="▼ Hide Weight Calculation Breakdown")
            self.is_expanded = True


class ReportWindow(ctk.CTkToplevel):
    def __init__(self, parent, results, grand_total_wt, grand_total_scrap):
        super().__init__(parent)
        self.title("Bill of Materials - Report")
        self.geometry("1300x500") 
        
        title = ctk.CTkLabel(self, text="Project Bill of Materials", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(15, 10))
        
        self.table_frame = ctk.CTkScrollableFrame(self, width=1250, height=300)
        self.table_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        headers = ["S.No", "Item Profile", "Dimensions", "Quantity", "Bars/Sheets", "Scrap (%)", "Scrap (kg)", "Billed Weight", "Tonnage (MT)", "Audit"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=10, pady=5, sticky="w")
            
        separator = ctk.CTkFrame(self.table_frame, height=2, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=len(headers), sticky="ew", pady=5)
        
        for row_idx, res in enumerate(results, start=2):
            ctk.CTkLabel(self.table_frame, text=str(res['sno'])).grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=res['profile']).grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            
            dim_text = f"{res['length']:.0f} mm" if not res['is_plate'] else f"{res['length']}' x {res['width']}' ft"
            ctk.CTkLabel(self.table_frame, text=dim_text).grid(row=row_idx, column=2, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=str(res['qty'])).grid(row=row_idx, column=3, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=str(res['bars'])).grid(row=row_idx, column=4, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=f"{res['scrap_pct']} %", text_color="#f0ad4e").grid(row=row_idx, column=5, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{res['scrap_wt']:.2f} kg", text_color="#f0ad4e", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=6, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.table_frame, text=f"{res['billed_wt']:.2f} kg", text_color="#3a7ebf", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=7, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{res['tonnage']:.3f} MT", text_color="#5cb85c", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=8, padx=10, pady=5, sticky="w")
            
            btn = ctk.CTkButton(self.table_frame, text="🔍 Show Math", width=100, fg_color="#333333", hover_color="#444444", 
                                command=lambda r=res: self.open_audit(r))
            btn.grid(row=row_idx, column=9, padx=10, pady=5)

        total_frame = ctk.CTkFrame(self)
        total_frame.pack(fill="x", padx=20, pady=15)
        
        grand_tonnage = math.ceil((grand_total_wt / 1000.0) * 1000.0) / 1000.0
        
        scrap_lbl = ctk.CTkLabel(total_frame, text=f"TOTAL SCRAP: {grand_total_scrap:.2f} kg", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f0ad4e")
        scrap_lbl.pack(side="left", padx=20, pady=10)

        grand_lbl = ctk.CTkLabel(total_frame, text=f"GRAND TOTAL: {grand_total_wt:.2f} kg  ({grand_tonnage:.3f} MT)", font=ctk.CTkFont(size=18, weight="bold"), text_color="#28a745")
        grand_lbl.pack(side="right", padx=20, pady=10)

    def open_audit(self, res_data):
        MathWindow(self, res_data)


class SteelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Steel BOM Calculator")
        self.geometry("1080x600") 
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.rows = [] 
        
        self.header = ctk.CTkLabel(self, text="Steel Procurement List", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 5))
        
        self.sub = ctk.CTkLabel(self, text="Linear items are measured in Millimeters (mm). Plates are measured in Feet (ft).", text_color="gray")
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
        profile_dropdown = ctk.CTkComboBox(row_frame, variable=profile_var, values=current_profiles, width=180)
        profile_dropdown.pack(side="left", padx=10)
        
        qty_entry = ctk.CTkEntry(row_frame, placeholder_text="Quantity", width=75)
        qty_entry.pack(side="left", padx=10)
        
        len_entry = ctk.CTkEntry(row_frame, placeholder_text="Length (mm)", width=100)
        len_entry.pack(side="left", padx=10)

        wid_entry = ctk.CTkEntry(row_frame, width=100)
        wid_entry.pack(side="left", padx=10)
        
        scrap_entry = ctk.CTkEntry(row_frame, placeholder_text="Scrap (%)", width=85)
        scrap_entry.pack(side="left", padx=10)
        
        def update_ui_for_category(*args):
            choice = cat_var.get()
            new_profiles = PROFILE_DATA.get(choice, ["--"])
            profile_dropdown.configure(values=new_profiles)
            profile_var.set(new_profiles[0])
            
            if choice == "Plate" or choice == "Grating":
                len_entry.configure(placeholder_text="Length (ft)")
                wid_entry.configure(state="normal")
                wid_entry.delete(0, 'end')
                wid_entry.configure(placeholder_text="Width (ft)")
            else:
                len_entry.configure(placeholder_text="Length (mm)")
                wid_entry.configure(state="normal") 
                wid_entry.delete(0, 'end')
                wid_entry.configure(placeholder_text="--")
                wid_entry.configure(state="disabled")
                
        cat_dropdown.configure(command=update_ui_for_category)
        update_ui_for_category() 
        
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
                tkmb.showerror("Invalid Input", f"Item {idx+1} has invalid numbers. Use digits only.")
                return
                
            try:
                order = bom_core.OrderItems(prof, qty, length, width)
                res = calculator.calculate_item(order)
                
                unit_wt = profile_details.get(prof, {}).get("weight", 0.0)
                
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
                    "unit_wt": unit_wt,          
                    "base_wt": res.base_weight_kg,
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