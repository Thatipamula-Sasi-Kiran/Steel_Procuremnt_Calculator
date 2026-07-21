import customtkinter as ctk
import tkinter.messagebox as tkmb
from tkinter import simpledialog, filedialog
import tkinter as tk
import csv
import bom_core
import os
import sys

# STREAMING_CHUNK:Configuring system paths and database...
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
                    profile_details[name] = {"weight": weight, "cat": cat}
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {"Default": ["ISMB 100"]}
    return categories

PROFILE_DATA = load_profiles()
CATEGORY_NAMES = list(PROFILE_DATA.keys())

# STREAMING_CHUNK:Defining the Unreal Engine Blueprint Flowchart...
class BlueprintMathWindow(ctk.CTkToplevel):
    def __init__(self, parent, summary_item, drawing_sources):
        super().__init__(parent)
        self.title(f"Blueprint Math: {summary_item.profile_name}")
        self.geometry("1400x700")  # Wider window for detailed nodes
        self.attributes("-topmost", True)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = ctk.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.draw_grid()
        
        # Node setup - Widened for detailed math
        node_width = 440
        x_spacing = 520 
        y_spacing = 180
        
        col0_x = 50
        col1_x = col0_x + x_spacing
        col2_x = col1_x + x_spacing
        col3_x = col2_x + x_spacing
        
        total_sources = len(drawing_sources)
        center_y = max(300, (total_sources * y_spacing) / 2)
        
        source_out_pins = []
        
        # --- Column 0: Source Nodes (The Drawings) ---
        for i, src in enumerate(drawing_sources):
            y_pos = 50 + (i * y_spacing)
            if src.is_plate:
                area_per_piece = (src.length_mm * src.width_mm) / 1000000.0
                props = [
                    ("Inputs", f"{src.quantity} pieces at {src.length_mm:.0f}x{src.width_mm:.0f} mm"),
                    ("Step 1", f"Area per piece: ({src.length_mm:.0f} × {src.width_mm:.0f}) ÷ 1,000,000 = {area_per_piece:.4f} m²"),
                    ("Step 2", f"Total Area: {area_per_piece:.4f} m² × {src.quantity} pieces = {src.exact_total_length_or_area:.4f} m²")
                ]
            else:
                len_m = src.length_mm / 1000.0
                props = [
                    ("Inputs", f"{src.quantity} pieces at {src.length_mm:.0f} mm"),
                    ("Step 1", f"Convert Length: {src.length_mm:.0f} mm ÷ 1000 = {len_m:.2f} meters"),
                    ("Step 2", f"Total Length: {len_m:.2f} m × {src.quantity} pieces = {src.exact_total_length_or_area:.2f} meters")
                ]
                
            _, outs = self.draw_node(
                x=col0_x, y=y_pos, width=node_width,
                title=f"◆ Extract Drawing ({src.drawing_name})", header_color="#8b0000",
                in_pins=[], out_pins=["Data Out \u25B6"], properties=props
            )
            source_out_pins.append(outs["Data Out \u25B6"])
            
        # --- Column 1: Aggregator Node (The Convergence) ---
        agg_in_pins = [f"Item {i+1} \u25B6" for i in range(total_sources)]
        
        math_str = " + ".join([f"{src.exact_total_length_or_area:.2f}" if not src.is_plate else f"{src.exact_total_length_or_area:.4f}" for src in drawing_sources])
        unit = "meters" if not summary_item.is_plate else "m²"
        
        agg_props = [
            ("Action", "Gathering all cuts from drawings above..."),
            ("Math", f"{math_str} = {summary_item.grand_total_length_or_area:.4f} {unit}"),
            ("Result", f"Grand Total Needed = {summary_item.grand_total_length_or_area:.4f} {unit}")
        ]
        
        agg_ins, agg_outs = self.draw_node(
            x=col1_x, y=center_y - 80, width=node_width,
            title="ƒ Aggregate Data", header_color="#27ae60",
            in_pins=agg_in_pins, out_pins=["Total \u25B6"], properties=agg_props
        )
        
        # --- Column 2: Strategy Node (Procurement Logic) ---
        if summary_item.is_plate:
            sheet_area = 1.25 * 2.50 if "1250" in summary_item.recommended_plate_size else 1.50 * 6.30
            raw_sheets = summary_item.grand_total_length_or_area / sheet_area
            
            strat_props = [
                ("Rule", "Testing standard sheet sizes to find lowest scrap."),
                ("Winner", f"{summary_item.recommended_plate_size} is the most efficient."),
                ("Math", f"Area of 1 winner sheet = {sheet_area:.4f} m²"),
                ("Math", f"{summary_item.grand_total_length_or_area:.4f} m² ÷ {sheet_area:.4f} m² = {raw_sheets:.2f} sheets"),
                ("Rule", "Rounding up to nearest full sheet."),
                ("Result", f"We must order {summary_item.standard_bars_to_order} full sheets.")
            ]
        else:
            raw_bars = summary_item.grand_total_length_or_area / 12.0
            strat_props = [
                ("Rule", "We must buy full 12.0 meter bars from the market."),
                ("Math", f"{summary_item.grand_total_length_or_area:.2f} meters needed ÷ 12.0 m = {raw_bars:.2f} bars"),
                ("Rule", "You cannot buy a fraction of a bar. Rounding up."),
                ("Result", f"We must order {summary_item.standard_bars_to_order} full bars.")
            ]
            
        strat_ins, strat_outs = self.draw_node(
            x=col2_x, y=center_y - 80, width=node_width,
            title="➔ Exec Strategy", header_color="#2980b9",
            in_pins=["Total In \u25B6"], out_pins=["Order Data \u25B6"], properties=strat_props
        )
        
        # --- Column 3: Final Output Node (The Billing) ---
        if summary_item.is_plate:
             final_props = [
                ("Fact", f"This plate weighs {summary_item.unit_weight:.2f} kg per m²."),
                ("Math", f"{summary_item.standard_bars_to_order} sheets × {sheet_area:.4f} m² × {summary_item.unit_weight:.2f} kg/m² = {summary_item.commercial_weight_kg:.2f} kg"),
                ("Math", f"{summary_item.commercial_weight_kg:.2f} kg ÷ 1000 = {summary_item.tonnage_mt:.3f} Metric Tons (MT)")
            ]
        else:
            final_props = [
                ("Fact", f"A 12.0m bar weighs {summary_item.unit_weight:.2f} kg per meter."),
                ("Math", f"{summary_item.standard_bars_to_order} bars × 12.0 m × {summary_item.unit_weight:.2f} kg/m = {summary_item.commercial_weight_kg:.2f} kg"),
                ("Math", f"{summary_item.commercial_weight_kg:.2f} kg ÷ 1000 = {summary_item.tonnage_mt:.3f} Metric Tons (MT)")
            ]
            
        final_ins, _ = self.draw_node(
            x=col3_x, y=center_y - 80, width=node_width,
            title="⛁ Final Order", header_color="#404040",
            in_pins=["Order Data \u25B6"], out_pins=[], properties=final_props
        )
        
        # Draw Spline Connections
        for i, src_pin in enumerate(source_out_pins):
            target_pin = agg_ins[agg_in_pins[i]]
            self.draw_spline(src_pin, target_pin, color="#3498db")
            
        self.draw_spline(agg_outs["Total \u25B6"], strat_ins["Total In \u25B6"], color="#e67e22")
        self.draw_spline(strat_outs["Order Data \u25B6"], final_ins["Order Data \u25B6"], color="#9b59b6")
        
        self.canvas.configure(scrollregion=(0, 0, col3_x + node_width + 100, max(700, (total_sources * y_spacing) + 100)))

# STREAMING_CHUNK:Implementing the node rendering and bezier splines...
    def draw_grid(self):
        for i in range(0, 4000, 20):
            color = "#2a2a2a" if i % 100 == 0 else "#222222"
            self.canvas.create_line(i, 0, i, 4000, fill=color)
            self.canvas.create_line(0, i, 4000, i, fill=color)

    def draw_node(self, x, y, width, title, header_color, properties, in_pins, out_pins):
        header_h = 30
        row_h = 24
        
        pins_rows = max(len(in_pins), len(out_pins))
        prop_rows = len(properties)
        
        body_h = ((pins_rows + prop_rows) * row_h) + 20
        if pins_rows > 0 and prop_rows > 0:
            body_h += 10 # Extra visual gap between pins and properties
        if body_h < 50: body_h = 50
        
        self.canvas.create_rectangle(x+3, y+3, x+width+3, y+header_h+body_h+3, fill="#000000", outline="")
        self.canvas.create_rectangle(x, y, x+width, y+header_h+body_h, fill="#1c1c1e", outline="#000000", width=2)
        self.canvas.create_rectangle(x, y, x+width, y+header_h, fill=header_color, outline="#000000", width=2)
        self.canvas.create_text(x+10, y+15, text=title, fill="#ffffff", font=("Segoe UI", 10, "bold"), anchor="w")
        
        in_coords, out_coords = {}, {}
        pin_radius = 5
        current_y = y + header_h + 15
        
        # Draw Pins First
        for i in range(pins_rows):
            if i < len(in_pins):
                pin_name = in_pins[i]
                self.canvas.create_oval(x-pin_radius, current_y-pin_radius, x+pin_radius, current_y+pin_radius, fill="#00a8ff", outline="#000000", width=1.5)
                self.canvas.create_text(x+15, current_y, text=pin_name, fill="#ffffff", font=("Segoe UI", 8), anchor="w")
                in_coords[pin_name] = (x, current_y)

            if i < len(out_pins):
                pin_name = out_pins[i]
                self.canvas.create_oval(x+width-pin_radius, current_y-pin_radius, x+width+pin_radius, current_y+pin_radius, fill="#00a8ff", outline="#000000", width=1.5)
                self.canvas.create_text(x+width-15, current_y, text=pin_name, fill="#ffffff", font=("Segoe UI", 8), anchor="e")
                out_coords[pin_name] = (x+width, current_y)
                
            current_y += row_h

        if pins_rows > 0 and prop_rows > 0:
            current_y += 10 # Drop down safely below pins
            
        # Draw Properties (Left Aligned for readability of formulas)
        for p_name, p_val in properties:
            self.canvas.create_text(x+10, current_y, text=f"{p_name}: ", fill="#aaaaaa", font=("Segoe UI", 9, "bold"), anchor="w")
            # Calculate width of the label to offset the value text
            label_w = self.canvas.bbox(self.canvas.create_text(0, 0, text=f"{p_name}: ", font=("Segoe UI", 9, "bold")))[2]
            self.canvas.create_text(x+10+label_w, current_y, text=f"{p_val}", fill="#e2e8f0", font=("Consolas", 9), anchor="w")
            current_y += row_h

        return in_coords, out_coords

    def draw_spline(self, start_pt, end_pt, color):
        x1, y1 = start_pt
        x2, y2 = end_pt
        dist = abs(x2 - x1)
        cx1 = x1 + (dist * 0.5)
        cy1 = y1
        cx2 = x2 - (dist * 0.5)
        cy2 = y2
        self.canvas.create_line(x1, y1, cx1, cy1, cx2, cy2, x2, y2, smooth=True, fill="#000000", width=4)
        self.canvas.create_line(x1, y1, cx1, cy1, cx2, cy2, x2, y2, smooth=True, fill=color, width=2)


# STREAMING_CHUNK:Building the Multi-Tabbed Report Window and Exporter...
class ReportWindow(ctk.CTkToplevel):
    def __init__(self, parent, project_result):
        super().__init__(parent)
        self.title("Consolidated Project Bill of Materials")
        self.geometry("1150x650") 
        
        self.project_result = project_result
        self.drawings_dict = {}
        for item in project_result.drawing_items:
            if item.drawing_name not in self.drawings_dict:
                self.drawings_dict[item.drawing_name] = []
            self.drawings_dict[item.drawing_name].append(item)
        
        title = ctk.CTkLabel(self, text="Project Bill of Materials", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(15, 10))
        
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        summary_tab = self.tabs.add("Consolidated Summary")
        self.build_summary_tab(summary_tab, project_result.summary_items, project_result.grand_total_tonnage)
            
        for d_name, items in self.drawings_dict.items():
            d_tab = self.tabs.add(d_name)
            self.build_drawing_tab(d_tab, items)
            
        export_btn = ctk.CTkButton(self, text="💾 Export to Excel (CSV)", fg_color="#1f6b40", hover_color="#288752", 
                                   font=ctk.CTkFont(weight="bold"), command=self.export_to_csv)
        export_btn.pack(pady=(0, 15))

    def build_summary_tab(self, parent, summary_items, total_mt):
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        headers = ["Material", "Recommended Size", "Bars/Sheets to Order", "Billed Wt (kg)", "Tonnage (MT)", "Audit Trail"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(scroll, text=header, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=15, pady=5, sticky="w")
            
        for row_idx, res in enumerate(summary_items, start=1):
            ctk.CTkLabel(scroll, text=res.profile_name, font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=0, padx=15, pady=8, sticky="w")
            ctk.CTkLabel(scroll, text=res.recommended_plate_size).grid(row=row_idx, column=1, padx=15, pady=8, sticky="w")
            ctk.CTkLabel(scroll, text=str(res.standard_bars_to_order)).grid(row=row_idx, column=2, padx=15, pady=8, sticky="w")
            ctk.CTkLabel(scroll, text=f"{res.commercial_weight_kg:.2f} kg").grid(row=row_idx, column=3, padx=15, pady=8, sticky="w")
            ctk.CTkLabel(scroll, text=f"{res.tonnage_mt:.3f} MT", text_color="#5cb85c", font=ctk.CTkFont(weight="bold")).grid(row=row_idx, column=4, padx=15, pady=8, sticky="w")
            
            profile_drawings = [d for d in self.project_result.drawing_items if d.profile_name == res.profile_name]
            btn = ctk.CTkButton(scroll, text="🔀 Blueprint Math", width=120, fg_color="#3b82f6", hover_color="#2563eb", 
                                command=lambda r=res, sources=profile_drawings: BlueprintMathWindow(self, r, sources))
            btn.grid(row=row_idx, column=5, padx=15, pady=8)

        total_frame = ctk.CTkFrame(parent)
        total_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(total_frame, text=f"PROJECT GRAND TOTAL: {total_mt:.3f} MT", font=ctk.CTkFont(size=18, weight="bold"), text_color="#28a745").pack(side="right", padx=20, pady=10)

    def build_drawing_tab(self, parent, drawing_items):
        scroll = ctk.CTkScrollableFrame(parent)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        headers = ["Material", "Thk", "Width (mm)", "Length (mm)", "Qty", "Total Len/Area", "Raw Cut Wt (kg)"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(scroll, text=header, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=col_idx, padx=15, pady=5, sticky="w")
            
        for row_idx, res in enumerate(drawing_items, start=1):
            ctk.CTkLabel(scroll, text=res.profile_name).grid(row=row_idx, column=0, padx=15, pady=5, sticky="w")
            ctk.CTkLabel(scroll, text="-").grid(row=row_idx, column=1, padx=15, pady=5, sticky="w") 
            w_text = f"{res.width_mm:.0f}" if res.is_plate else "-"
            ctk.CTkLabel(scroll, text=w_text).grid(row=row_idx, column=2, padx=15, pady=5, sticky="w")
            ctk.CTkLabel(scroll, text=f"{res.length_mm:.0f}").grid(row=row_idx, column=3, padx=15, pady=5, sticky="w")
            ctk.CTkLabel(scroll, text=str(res.quantity)).grid(row=row_idx, column=4, padx=15, pady=5, sticky="w")
            
            amt_text = f"{res.exact_total_length_or_area:.4f} m²" if res.is_plate else f"{res.exact_total_length_or_area:.2f} m"
            ctk.CTkLabel(scroll, text=amt_text).grid(row=row_idx, column=5, padx=15, pady=5, sticky="w")
            ctk.CTkLabel(scroll, text=f"{res.exact_weight_kg:.2f} kg").grid(row=row_idx, column=6, padx=15, pady=5, sticky="w")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")], title="Save Project BOM")
        if not file_path: return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write Individual Drawings
                for d_name, items in self.drawings_dict.items():
                    writer.writerow([f"--- DRAWING: {d_name.upper()} ---"])
                    writer.writerow(["Material", "Thk", "Width (mm)", "Length (mm)", "Qty", "Total Len/Area", "Raw Cut Wt (kg)"])
                    for res in items:
                        w_text = f"{res.width_mm:.0f}" if res.is_plate else "-"
                        amt_text = f"{res.exact_total_length_or_area:.4f} m²" if res.is_plate else f"{res.exact_total_length_or_area:.2f} m"
                        writer.writerow([res.profile_name, "-", w_text, f"{res.length_mm:.0f}", res.quantity, amt_text, round(res.exact_weight_kg, 2)])
                    writer.writerow([]) # Empty row for spacing
                    
                # Write Summary
                writer.writerow(["--- CONSOLIDATED PROCUREMENT SUMMARY ---"])
                writer.writerow(["Material", "Recommended Size", "Bars/Sheets to Order", "Billed Wt (kg)", "Tonnage (MT)"])
                for res in self.project_result.summary_items:
                    writer.writerow([res.profile_name, res.recommended_plate_size, res.standard_bars_to_order, round(res.commercial_weight_kg, 2), round(res.tonnage_mt, 3)])
                    
                writer.writerow([])
                writer.writerow(["", "", "", "PROJECT GRAND TOTAL (MT):", round(self.project_result.grand_total_tonnage, 3)])
                
            tkmb.showinfo("Export Successful", f"BOM successfully saved to:\n{file_path}")
        except Exception as e:
            tkmb.showerror("Export Error", f"Failed to save file:\n{e}")

# STREAMING_CHUNK:Building the Multi-Tiered Tabbed App...
class SteelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Steel BOM Project Manager")
        self.geometry("1100x650") 
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.drawings = {}
        
        self.header = ctk.CTkLabel(self, text="Multi-Tiered Procurement System", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(pady=(20, 5))
        
        self.sub = ctk.CTkLabel(self, text="All measurements (Length & Width) must be strictly in Millimeters (mm).", text_color="gray")
        self.sub.pack(pady=(0, 10))
        
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20)
        
        ctk.CTkButton(ctrl_frame, text="+ Add Drawing", command=self.add_drawing_tab, width=120).pack(side="left", padx=5)
        ctk.CTkButton(ctrl_frame, text="✏️ Rename Current", command=self.rename_current_tab, width=120, fg_color="#555555").pack(side="left", padx=5)
        
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=15)
        
        self.calc_btn = ctk.CTkButton(self.btn_frame, text="Generate Project BOM", command=self.calculate_all, height=45, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#10b981", hover_color="#059669")
        self.calc_btn.pack(side="right", padx=10)
        
        self.add_drawing_tab("Drawing 1")

    def add_drawing_tab(self, name=None):
        if not name:
            name = simpledialog.askstring("New Drawing", "Enter Drawing Name:")
            if not name:
                return
                
        if name in self.drawings:
            tkmb.showerror("Error", "A drawing with that name already exists.")
            return
            
        tab_frame = self.tabs.add(name)
        self.tabs.set(name)
        
        scroll_frame = ctk.CTkScrollableFrame(tab_frame)
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(tab_frame, text="+ Add Item to " + name, command=lambda d=name: self.add_item_row(d), fg_color="#444444", hover_color="#555555")
        add_btn.pack(pady=10)
        
        self.drawings[name] = {"scroll": scroll_frame, "rows": []}
        self.add_item_row(name)

    def rename_current_tab(self):
        old_name = self.tabs.get()
        new_name = simpledialog.askstring("Rename Drawing", "Enter New Drawing Name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
            
        if new_name in self.drawings:
            tkmb.showerror("Error", "A drawing with that name already exists.")
            return
            
        tkmb.showinfo("Info", "Tab renaming requires a UI rebuild. Feature coming soon. Please create a new tab for now!")

    def add_item_row(self, drawing_name):
        d_data = self.drawings[drawing_name]
        row_frame = ctk.CTkFrame(d_data["scroll"])
        row_frame.pack(fill="x", pady=5)
        
        sno_lbl = ctk.CTkLabel(row_frame, text=f"{len(d_data['rows']) + 1}.")
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
        
        def update_ui_for_category(*args):
            choice = cat_var.get()
            new_profiles = PROFILE_DATA.get(choice, ["--"])
            profile_dropdown.configure(values=new_profiles)
            profile_var.set(new_profiles[0])
            
            if choice == "Plate" or choice == "Grating":
                wid_entry.configure(state="normal")
                wid_entry.delete(0, 'end')
                wid_entry.configure(placeholder_text="Width (mm)")
            else:
                wid_entry.configure(state="normal") 
                wid_entry.delete(0, 'end')
                wid_entry.configure(placeholder_text="-")
                wid_entry.configure(state="disabled")
                
        cat_dropdown.configure(command=update_ui_for_category)
        update_ui_for_category() 
        
        row_data = {
            "frame": row_frame,
            "sno_lbl": sno_lbl,
            "profile": profile_var,
            "qty": qty_entry,
            "length": len_entry,
            "width": wid_entry
        }
        
        def remove_self():
            row_frame.destroy()
            d_data["rows"].remove(row_data)
            for idx, r in enumerate(d_data["rows"]):
                r["sno_lbl"].configure(text=f"{idx + 1}.")
            
        remove_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="#ef4444", hover_color="#dc2626", command=remove_self)
        remove_btn.pack(side="right", padx=10)
        
        d_data["rows"].append(row_data)

    def calculate_all(self):
        project_items = []
        
        for d_name, d_data in self.drawings.items():
            for idx, row in enumerate(d_data["rows"]):
                prof = row["profile"].get()
                qty_str = row["qty"].get()
                len_str = row["length"].get()
                wid_str = row["width"].get()
                
                if not qty_str and not len_str:
                    continue
                    
                is_plate = profile_details.get(prof, {}).get("cat") in ["Plate", "Grating"]
                
                if not qty_str or not len_str:
                    tkmb.showerror("Missing Data", f"[{d_name}] Item {idx+1} is missing Quantity or Length.")
                    return
                if is_plate and not wid_str:
                    tkmb.showerror("Missing Data", f"[{d_name}] Item {idx+1} is a Plate and requires a Width (mm).")
                    return
                    
                try:
                    qty = int(qty_str)
                    length = float(len_str)
                    width = float(wid_str) if is_plate else 0.0
                except ValueError:
                    tkmb.showerror("Invalid Input", f"[{d_name}] Item {idx+1} has invalid numbers.")
                    return
                    
                order = bom_core.OrderItems(d_name, prof, qty, length, width)
                project_items.append(order)
                
        if not project_items:
            tkmb.showwarning("Empty Project", "Please add at least one item with data.")
            return

        try:
            project_result = calculator.calculate_project(project_items)
            ReportWindow(self, project_result)
        except Exception as e:
            tkmb.showerror("C++ Engine Error", f"Fatal calculation error:\n{e}")

if __name__ == "__main__":
    app = SteelApp()
    app.mainloop()