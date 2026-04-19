import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import shutil
from datetime import datetime

# ─── Konstante boja ───────────────────────────────────────────────
BG_COLOR      = "#1a1a2e"
ACCENT_COLOR  = "#16213e"
BTN_COLOR     = "#e94560"
BTN_HOVER     = "#c73652"
TEXT_COLOR    = "#ffffff"
ENTRY_BG      = "#0f3460"
SUCCESS_COLOR = "#2ecc71"
ERROR_COLOR   = "#e74c3c"
HEADER_COLOR  = "#e94560"
TREE_BG       = "#16213e"
TREE_SELECT   = "#e94560"

FONT        = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 11, "bold")
FONT_HEADER = ("Segoe UI", 18, "bold")

CSV_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medical_students_dataset.csv")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")

COLUMNS = [
    "Student ID", "Age", "Gender", "Height", "Weight",
    "Blood Type", "BMI", "Temperature", "Heart Rate",
    "Blood Pressure", "Cholesterol", "Diabetes", "Smoking",
]

# Srpski nazivi kolona za prikaz u formi
LABELS = {
    "Student ID":    "Student ID",
    "Age":           "Godine (18-40)",
    "Gender":        "Pol",
    "Height":        "Visina cm",
    "Weight":        "Tezina kg",
    "Blood Type":    "Krvna grupa",
    "BMI":           "BMI (auto)",
    "Temperature":   "Temperatura F",
    "Heart Rate":    "Otkucaji srca (bpm)",
    "Blood Pressure":"Krvni pritisak (mmHg)",
    "Cholesterol":   "Holesterol (mg/dL)",
    "Diabetes":      "Dijabetes",
    "Smoking":       "Pusenje",
}

DROPDOWN_OPTIONS = {
    "Gender":     ["Male", "Female"],
    "Blood Type": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "Diabetes":   ["Yes", "No"],
    "Smoking":    ["Yes", "No"],
}


class MedicalStudentApp(tk.Tk):
    """Glavna aplikacija za upravljanje podacima medicinskih studenata."""

    def __init__(self):
        """Inicijalizacija prozora i svih GUI komponenti."""
        super().__init__()
        self.title("Medical Students Management System")
        self.minsize(1200, 700)
        self.configure(bg=BG_COLOR)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)

        self.data: list[dict]          = []
        self.filtered_data: list[dict] = []
        self.added_students: list[dict] = []
        self.added_window: "AddedStudentsWindow | None" = None
        self.selected_id: str | None   = None
        self.search_var      = tk.StringVar()
        self.filter_var      = tk.StringVar(value="Sve")
        self.filter_value_var = tk.StringVar(value="Sve")

        self.create_header()
        self.create_search_bar()
        self.create_main_area()
        self.create_bottom_panel()

        self.load_data()

    # ─── CSV operacije ────────────────────────────────────────────

    def load_data(self):
        """Ucitaj podatke iz CSV fajla u self.data."""
        try:
            with open(CSV_FILE, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.data = [self._normalize_row(row) for row in reader]
        except FileNotFoundError:
            self.data = []
            self.show_message("CSV fajl nije pronadjen. Prazan dataset.", error=False)
        self.filtered_data = list(self.data)
        self.refresh_table()
        self.update_statistics()

    def save_data(self):
        """Napravi backup i sacuvaj self.data u CSV."""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if os.path.exists(CSV_FILE):
            shutil.copy2(CSV_FILE, os.path.join(BACKUP_DIR, f"backup_{ts}.csv"))
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.data)

    def add_student(self):
        """Validiraj formu, generisi StudentID i dodaj studenta u CSV."""
        values = self._get_form_values()
        if values is None:
            return
        existing = []
        for r in self.data:
            try:
                existing.append(int(float(r.get("Student ID") or 0)))
            except (ValueError, TypeError):
                pass
        values["Student ID"] = str(max(existing, default=0) + 1)
        self.data.append(values)
        self.added_students.append(values)
        self.save_data()
        self._sync_and_refresh()
        self.clear_form()
        self.show_message("Student uspjesno dodan!", error=False)
        self._open_or_refresh_added_window()

    def update_student(self):
        """Zamijeni zapis odabranog studenta podacima iz forme."""
        if self.selected_id is None:
            self.show_message("Odaberite studenta iz tabele.", error=True)
            return
        values = self._get_form_values()
        if values is None:
            return
        values["Student ID"] = self.selected_id
        for i, row in enumerate(self.data):
            if str(row.get("Student ID", "")).strip() == str(self.selected_id).strip():
                self.data[i] = values
                break
        self.save_data()
        self._sync_and_refresh()
        self.clear_form()
        self.show_message("Student uspjesno azuriran!", error=False)

    def delete_student(self):
        """Obrisi odabranog studenta nakon potvrde."""
        if self.selected_id is None:
            self.show_message("Odaberite studenta iz tabele.", error=True)
            return
        if not messagebox.askyesno(
            "Potvrda brisanja",
            f"Obrisati studenta ID={self.selected_id}?",
        ):
            return
        self.data = [
            r for r in self.data
            if str(r.get("Student ID", "")).strip() != str(self.selected_id).strip()
        ]
        self.save_data()
        self._sync_and_refresh()
        self.clear_form()
        self.show_message("Student uspjesno obrisan!", error=False)

    def search_students(self, *_):
        """Filtriraj tabelu u realnom vremenu po pretrazi i filteru."""
        query      = self.search_var.get().lower().strip()
        filter_cat = self.filter_var.get()
        filter_val = self.filter_value_var.get()

        result = self.data
        if query:
            result = [
                r for r in result
                if query in str(r.get("Student ID", "")).lower()
                or query in str(r.get("Gender", "")).lower()
                or query in str(r.get("Blood Type", "")).lower()
            ]
        col_map = {
            "Pol":        "Gender",
            "Krvna grupa":"Blood Type",
            "Dijabetes":  "Diabetes",
            "Pusenje":    "Smoking",
        }
        if filter_cat != "Sve" and filter_val != "Sve":
            col = col_map.get(filter_cat)
            if col:
                result = [r for r in result if str(r.get(col, "")).strip() == filter_val]

        self.filtered_data = result
        self.refresh_table()

    # ─── Kreiranje GUI-a ──────────────────────────────────────────

    def create_header(self):
        """Red 0: naslov koji se proteze punom sirinom."""
        frame = tk.Frame(self, bg=ACCENT_COLOR, pady=12)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Medical Students Management System",
                 font=FONT_HEADER, bg=ACCENT_COLOR, fg=HEADER_COLOR,
                 ).grid(row=0, column=0)

    def create_search_bar(self):
        """Red 1: polje za pretragu, filter dropdown i dugme Reset."""
        bar = tk.Frame(self, bg=BG_COLOR, pady=8)
        bar.grid(row=1, column=0, sticky="ew", padx=15)
        bar.columnconfigure(1, weight=1)

        tk.Label(bar, text="Pretraga (ID / Pol / Krvna grupa):",
                 bg=BG_COLOR, fg=TEXT_COLOR, font=FONT,
                 ).grid(row=0, column=0, padx=(0, 6))

        tk.Entry(bar, textvariable=self.search_var,
                 bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                 font=FONT, relief="flat", bd=5,
                 ).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.search_var.trace_add("write", self.search_students)

        tk.Label(bar, text="Filter:", bg=BG_COLOR, fg=TEXT_COLOR,
                 font=FONT).grid(row=0, column=2, padx=(0, 5))

        self.filter_combo = ttk.Combobox(
            bar, textvariable=self.filter_var,
            values=["Sve", "Pol", "Krvna grupa", "Dijabetes", "Pusenje"],
            state="readonly", width=18, font=FONT,
        )
        self.filter_combo.grid(row=0, column=3, padx=(0, 5))
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_cat_change)

        self.filter_value_combo = ttk.Combobox(
            bar, textvariable=self.filter_value_var,
            values=["Sve"], state="readonly", width=14, font=FONT,
        )
        self.filter_value_combo.grid(row=0, column=4, padx=(0, 10))
        self.filter_value_combo.bind("<<ComboboxSelected>>", self.search_students)

        reset_btn = tk.Button(bar, text="Reset", bg=BTN_COLOR, fg=TEXT_COLOR,
                              font=FONT_BOLD, relief="flat", cursor="hand2",
                              command=self.reset_search, padx=12, pady=4)
        reset_btn.grid(row=0, column=5)
        self._bind_hover(reset_btn)

    def create_main_area(self):
        """Red 2: lijeva forma + desna tabela."""
        main = tk.Frame(self, bg=BG_COLOR)
        main.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)
        self.create_form(main)
        self.create_table(main)

    def create_form(self, parent: tk.Frame):
        """Lijeva kolona reda 2: forma za unos podataka."""
        frame = tk.LabelFrame(
            parent, text=" Podaci o studentu ",
            bg=ACCENT_COLOR, fg=HEADER_COLOR, font=FONT_BOLD,
            bd=2, relief="groove", padx=10, pady=10,
        )
        frame.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        self.form_vars: dict[str, tk.StringVar] = {}

        # Redoslijed polja u formi (key, dropdown opcije ili None za Entry)
        # BMI se ne unosi - izracunava se automatski
        fields = [
            ("Age",            None),
            ("Gender",         DROPDOWN_OPTIONS["Gender"]),
            ("Height",         None),
            ("Weight",         None),
            ("Blood Type",     DROPDOWN_OPTIONS["Blood Type"]),
            ("Temperature",    None),
            ("Heart Rate",     None),
            ("Blood Pressure", None),
            ("Cholesterol",    None),
            ("Diabetes",       DROPDOWN_OPTIONS["Diabetes"]),
            ("Smoking",        DROPDOWN_OPTIONS["Smoking"]),
        ]

        for i, (key, opts) in enumerate(fields):
            tk.Label(frame, text=LABELS[key] + ":", bg=ACCENT_COLOR,
                     fg=TEXT_COLOR, font=FONT, anchor="w",
                     ).grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar()
            self.form_vars[key] = var
            if opts:
                w = ttk.Combobox(frame, textvariable=var, values=opts,
                                 state="readonly", width=18, font=FONT)
            else:
                w = tk.Entry(frame, textvariable=var, bg=ENTRY_BG,
                             fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                             font=FONT, relief="flat", bd=4, width=20)
            w.grid(row=i, column=1, sticky="ew", padx=(8, 0), pady=3)

        n = len(fields)
        self.msg_label = tk.Label(frame, text="", bg=ACCENT_COLOR,
                                  font=("Segoe UI", 9), wraplength=270)
        self.msg_label.grid(row=n, column=0, columnspan=2, pady=(8, 0))

        self.id_label = tk.Label(frame, text="Student ID: —",
                                 bg=ACCENT_COLOR, fg="#aaaaaa",
                                 font=("Segoe UI", 9, "italic"))
        self.id_label.grid(row=n + 1, column=0, columnspan=2)

    def create_table(self, parent: tk.Frame):
        """Desna kolona reda 2: Treeview tabela sa scrollbarovima."""
        frame = tk.Frame(parent, bg=ACCENT_COLOR)
        frame.grid(row=0, column=1, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("M.Treeview",
                         background=TREE_BG, foreground=TEXT_COLOR,
                         fieldbackground=TREE_BG, rowheight=25,
                         font=("Segoe UI", 9))
        style.configure("M.Treeview.Heading",
                         background=ACCENT_COLOR, foreground=HEADER_COLOR,
                         font=("Segoe UI", 9, "bold"))
        style.map("M.Treeview", background=[("selected", TREE_SELECT)])

        col_widths = {
            "StudentID": 70, "Gender": 65, "Age": 45, "Ethnicity": 100,
            "Year": 50, "University": 160, "GPA": 55, "MCAT Score": 85,
            "Clinical Experience": 120, "Research Experience": 130,
            "Publication Count": 110, "Exam Score": 90,
        }
        self.tree = ttk.Treeview(frame, columns=COLUMNS,
                                  show="headings", style="M.Treeview")
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 90), anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    def create_statistics(self):
        """Red 3 (gornji dio): traka sa agregatnim statistikama."""
        pass  # implementirano unutar create_bottom_panel

    def create_buttons(self):
        """Red 3 (donji dio): akcijska dugmad."""
        pass  # implementirano unutar create_bottom_panel

    def create_bottom_panel(self):
        """Red 3: prikvaceni donji panel sa statistikama i dugmadima."""
        panel = tk.Frame(self, bg=ACCENT_COLOR)
        panel.grid(row=3, column=0, sticky="ew")
        panel.columnconfigure(0, weight=1)

        # ── Statistike ──
        stats_frame = tk.Frame(panel, bg=ACCENT_COLOR, pady=6)
        stats_frame.grid(row=0, column=0, sticky="ew", padx=15)
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_labels: dict[str, tk.Label] = {}
        stats = [
            ("total",    "Ukupno studenata"),
            ("avg_bmi",  "Prosjecni BMI"),
            ("avg_hr",   "Prosjecni otkucaji srca"),
            ("avg_temp", "Prosjecna temperatura (F)"),
        ]
        for i, (key, label) in enumerate(stats):
            cell = tk.Frame(stats_frame, bg=ACCENT_COLOR)
            cell.grid(row=0, column=i, padx=10)
            tk.Label(cell, text=label, bg=ACCENT_COLOR, fg="#aaaaaa",
                     font=("Segoe UI", 8)).grid(row=0, column=0)
            lbl = tk.Label(cell, text="—", bg=ACCENT_COLOR, fg=HEADER_COLOR,
                           font=("Segoe UI", 13, "bold"))
            lbl.grid(row=1, column=0)
            self.stat_labels[key] = lbl

        # ── Dugmad ──
        btn_frame = tk.Frame(panel, bg=BG_COLOR, pady=8)
        btn_frame.grid(row=1, column=0, sticky="ew")
        btn_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        for i, (text, cmd) in enumerate([
            ("+ Dodaj studenta",  self.add_student),
            ("Azuriraj",          self.update_student),
            ("Obrisi",            self.delete_student),
            ("Ocisti formu",      self.clear_form),
        ]):
            btn = tk.Button(btn_frame, text=text, command=cmd,
                            bg=BTN_COLOR, fg=TEXT_COLOR, font=FONT_BOLD,
                            relief="flat", cursor="hand2", padx=20, pady=8)
            btn.grid(row=0, column=i, padx=8, pady=4)
            self._bind_hover(btn)

        self.added_btn = tk.Button(
            btn_frame, text="Dodani studenti (0)",
            command=self._open_or_refresh_added_window,
            bg="#0f3460", fg=TEXT_COLOR, font=FONT_BOLD,
            relief="flat", cursor="hand2", padx=20, pady=8,
        )
        self.added_btn.grid(row=0, column=4, padx=8, pady=4)
        self.added_btn.bind("<Enter>", lambda _: self.added_btn.config(bg="#1a4a80"))
        self.added_btn.bind("<Leave>", lambda _: self.added_btn.config(bg="#0f3460"))

    # ─── Pomocne GUI metode ───────────────────────────────────────

    def refresh_table(self):
        """Ocisti Treeview i ponovo ga popuni iz filtered_data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.filtered_data:
            self.tree.insert("", "end", values=[row.get(c, "") for c in COLUMNS])

    def populate_form(self, row: dict):
        """Popuni polja forme podacima iz odabranog reda tabele."""
        for key in self.form_vars:
            self.form_vars[key].set(row.get(key, ""))
        sid = row.get("Student ID", "")
        self.selected_id = sid
        self.id_label.config(text=f"Student ID: {sid}")
        self.msg_label.config(text="")

    def clear_form(self):
        """Resetuj sva polja forme i ponisti selekciju."""
        for var in self.form_vars.values():
            var.set("")
        self.selected_id = None
        self.id_label.config(text="Student ID: —")
        self.msg_label.config(text="")

    def update_statistics(self):
        """Preracunaj i azuriraj labele statistika."""
        total = len(self.data)
        self.stat_labels["total"].config(text=str(total))
        if total == 0:
            for key in ("avg_bmi", "avg_hr", "avg_temp"):
                self.stat_labels[key].config(text="—")
            return

        def avg(col: str) -> float:
            vals = []
            for r in self.data:
                try:
                    vals.append(float(r.get(col) or ""))
                except (ValueError, TypeError):
                    pass
            return sum(vals) / len(vals) if vals else 0.0

        self.stat_labels["avg_bmi"].config(text=f"{avg('BMI'):.1f}")
        self.stat_labels["avg_hr"].config(text=f"{avg('Heart Rate'):.1f}")
        self.stat_labels["avg_temp"].config(text=f"{int(round(avg('Temperature')))}")

    def show_message(self, text: str, error: bool = True):
        """Prikazi poruku ispod forme 4 sekunde."""
        self.msg_label.config(text=text,
                               fg=ERROR_COLOR if error else SUCCESS_COLOR)
        self.after(4000, lambda: self.msg_label.config(text=""))

    def reset_search(self):
        """Ocisti pretragu i filter, prikazi sve zapise."""
        self.search_var.set("")
        self.filter_var.set("Sve")
        self.filter_value_var.set("Sve")
        self.filter_value_combo.config(values=["Sve"])
        self.filtered_data = list(self.data)
        self.refresh_table()

    # ─── Privatne pomocne metode ──────────────────────────────────

    def _sync_and_refresh(self):
        """Kopiraj data → filtered_data i osvjezi tabelu i statistike."""
        self.filtered_data = list(self.data)
        self.refresh_table()
        self.update_statistics()

    def _on_row_select(self, _event):
        """Popuni formu pri kliku na red u Treeview-u."""
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.populate_form(dict(zip(COLUMNS, values)))

    def _on_filter_cat_change(self, _event=None):
        """Obnovi dropdown vrijednosti filtera pri promjeni kategorije."""
        cat = self.filter_var.get()
        col_map = {
            "Pol":        "Gender",
            "Krvna grupa":"Blood Type",
            "Dijabetes":  "Diabetes",
            "Pusenje":    "Smoking",
        }
        col = col_map.get(cat)
        if col:
            unique = sorted({
                str(r.get(col, "")).strip()
                for r in self.data if str(r.get(col, "")).strip()
            })
            self.filter_value_combo.config(values=["Sve"] + unique)
        else:
            self.filter_value_combo.config(values=["Sve"])
        self.filter_value_var.set("Sve")

    def _get_form_values(self) -> dict | None:
        """Validiraj unos iz forme; vrati dict ili None pri gresci."""
        v = {k: var.get().strip() for k, var in self.form_vars.items()}

        # Provjera praznih polja (BMI se ne unosi)
        for key in self.form_vars:
            if not v[key]:
                self.show_message(f"Polje '{LABELS[key]}' je obavezno.", error=True)
                return None

        try:
            age = int(v["Age"])
            assert 18 <= age <= 40
        except (ValueError, AssertionError):
            self.show_message("Godine moraju biti cijeli broj 18-40.", error=True)
            return None

        try:
            height = int(round(float(v["Height"])))
            assert height > 0
        except (ValueError, AssertionError):
            self.show_message("Visina mora biti pozitivan broj (cm).", error=True)
            return None

        try:
            weight = int(round(float(v["Weight"])))
            assert weight > 0
        except (ValueError, AssertionError):
            self.show_message("Tezina mora biti pozitivan broj (kg).", error=True)
            return None

        try:
            temp = int(round(float(v["Temperature"])))
            assert 90 <= temp <= 110
        except (ValueError, AssertionError):
            self.show_message("Temperatura mora biti cijeli broj 90-110 F.", error=True)
            return None

        try:
            hr = int(v["Heart Rate"])
            assert 30 <= hr <= 250
        except (ValueError, AssertionError):
            self.show_message("Otkucaji srca moraju biti cijeli broj 30-250.", error=True)
            return None

        try:
            bp = int(round(float(v["Blood Pressure"])))
            assert bp > 0
        except (ValueError, AssertionError):
            self.show_message("Krvni pritisak mora biti pozitivan broj.", error=True)
            return None

        try:
            chol = int(v["Cholesterol"])
            assert chol > 0
        except (ValueError, AssertionError):
            self.show_message("Holesterol mora biti pozitivan cijeli broj.", error=True)
            return None

        bmi = self._compute_bmi(str(height), str(weight))

        return {
            "Student ID":    "",
            "Age":           str(age),
            "Gender":        v["Gender"],
            "Height":        str(height),
            "Weight":        str(weight),
            "Blood Type":    v["Blood Type"],
            "BMI":           bmi,
            "Temperature":   str(temp),
            "Heart Rate":    str(hr),
            "Blood Pressure":str(bp),
            "Cholesterol":   str(chol),
            "Diabetes":      v["Diabetes"],
            "Smoking":       v["Smoking"],
        }

    def _compute_bmi(self, height_str: str, weight_str: str) -> str:
        """Izracunaj BMI iz visine (cm) i tezine (kg) kao cijeli broj."""
        try:
            h = float(height_str) / 100
            w = float(weight_str)
            return str(int(round(w / (h * h))))
        except (ValueError, ZeroDivisionError):
            return ""

    def _normalize_row(self, row: dict) -> dict:
        """Zaokruzi Height, Weight, BMI i Temperature na cijele brojeve."""
        for col in ("Height", "Weight", "BMI", "Temperature"):
            val = row.get(col, "")
            try:
                row[col] = str(int(round(float(val))))
            except (ValueError, TypeError):
                row[col] = val
        return row

    def _open_or_refresh_added_window(self):
        """Otvori ili osvjezi prozor dodanih studenata."""
        n = len(self.added_students)
        self.added_btn.config(text=f"Dodani studenti ({n})")
        if self.added_window is None or not self.added_window.winfo_exists():
            self.added_window = AddedStudentsWindow(self)
        else:
            self.added_window.refresh(self.added_students)
            self.added_window.lift()

    def _bind_hover(self, btn: tk.Button):
        """Dodaj hover efekat na dugme."""
        btn.bind("<Enter>", lambda _: btn.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda _: btn.config(bg=BTN_COLOR))


class AddedStudentsWindow(tk.Toplevel):
    """Poseban prozor koji prikazuje studente dodane u tekucoj sesiji."""

    def __init__(self, parent: MedicalStudentApp):
        """Otvori prozor sa poljem za svrhu liste, tabelom i dugmetom za brisanje."""
        super().__init__(parent)
        self._parent = parent
        self.title("Lista dodanih studenata")
        self.configure(bg=BG_COLOR)
        self.minsize(1100, 420)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # ── Red 0: naslov prozora ──
        hdr = tk.Frame(self, bg=ACCENT_COLOR, pady=8)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(0, weight=1)
        tk.Label(hdr, text="Lista dodanih studenata",
                 font=FONT_HEADER, bg=ACCENT_COLOR, fg=HEADER_COLOR,
                 ).grid(row=0, column=0)

        # ── Red 1: polje za svrhu liste ──
        purpose_frame = tk.Frame(self, bg=BG_COLOR, pady=6)
        purpose_frame.grid(row=1, column=0, sticky="ew", padx=15)
        purpose_frame.columnconfigure(1, weight=1)

        tk.Label(purpose_frame, text="Svrha liste:", bg=BG_COLOR,
                 fg=TEXT_COLOR, font=FONT_BOLD,
                 ).grid(row=0, column=0, padx=(0, 8))
        self._purpose_var = tk.StringVar()
        tk.Entry(purpose_frame, textvariable=self._purpose_var,
                 bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                 font=FONT, relief="flat", bd=5,
                 ).grid(row=0, column=1, sticky="ew")

        self._count_lbl = tk.Label(purpose_frame, text="", bg=BG_COLOR,
                                   fg="#aaaaaa", font=("Segoe UI", 9))
        self._count_lbl.grid(row=0, column=2, padx=(12, 0))

        # ── Red 2: tabela ──
        frame = tk.Frame(self, bg=ACCENT_COLOR)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        col_widths = {
            "Student ID": 70, "Age": 45, "Gender": 65, "Height": 65,
            "Weight": 60, "Blood Type": 80, "BMI": 55, "Temperature": 85,
            "Heart Rate": 85, "Blood Pressure": 105, "Cholesterol": 90,
            "Diabetes": 70, "Smoking": 70,
        }
        self._tree = ttk.Treeview(frame, columns=COLUMNS,
                                   show="headings", style="M.Treeview")
        for col in COLUMNS:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=col_widths.get(col, 80), anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # ── Red 3: dugmad ──
        btn_frame = tk.Frame(self, bg=BG_COLOR, pady=8)
        btn_frame.grid(row=3, column=0)

        del_btn = tk.Button(btn_frame, text="Obrisi odabrano",
                            command=self._delete_selected,
                            bg=BTN_COLOR, fg=TEXT_COLOR, font=FONT_BOLD,
                            relief="flat", cursor="hand2", padx=20, pady=6)
        del_btn.grid(row=0, column=0, padx=8)
        del_btn.bind("<Enter>", lambda _: del_btn.config(bg=BTN_HOVER))
        del_btn.bind("<Leave>", lambda _: del_btn.config(bg=BTN_COLOR))

        close_btn = tk.Button(btn_frame, text="Zatvori", command=self.destroy,
                              bg="#0f3460", fg=TEXT_COLOR, font=FONT_BOLD,
                              relief="flat", cursor="hand2", padx=20, pady=6)
        close_btn.grid(row=0, column=1, padx=8)
        close_btn.bind("<Enter>", lambda _: close_btn.config(bg="#1a4a80"))
        close_btn.bind("<Leave>", lambda _: close_btn.config(bg="#0f3460"))

        self.refresh(parent.added_students)

    def refresh(self, students: list[dict]):
        """Ponovo popuni tabelu sa zadatom listom studenata."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        for row in students:
            self._tree.insert("", "end", values=[row.get(c, "") for c in COLUMNS])
        self._count_lbl.config(text=f"({len(students)} studenata)")

    def _delete_selected(self):
        """Obrisi odabrani red iz liste i iz parent.added_students."""
        sel = self._tree.selection()
        if not sel:
            return
        values = self._tree.item(sel[0], "values")
        sid = values[0]
        self._parent.added_students = [
            r for r in self._parent.added_students
            if str(r.get("Student ID", "")).strip() != str(sid).strip()
        ]
        self._parent._open_or_refresh_added_window()
        self.refresh(self._parent.added_students)


if __name__ == "__main__":
    app = MedicalStudentApp()
    app.mainloop()
