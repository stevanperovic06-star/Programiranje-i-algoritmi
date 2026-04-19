 '''Medical Students Management System

Tkinter desktop aplikacija za upravljanje zdravstvenim podacima medicinskih studenata.



Uslovi

- Python 3.8+
- Standardna biblioteka: `tkinter`, `csv`, `os`, `shutil` (sve ukljuceno u Python)

Pokretanje

bash
cd projekat
python app.py





Uvod

Aplikacija je razvijena koristeci Anthropic Claude Code — AI coding agenta koji se pokrece
direktno iz terminala ili VS Code okruzenja. Umjesto klasicnog pisanja koda od nule, koristili
smo agentic workflow gdje Claude autonomno analizira, planira i implementira kod na osnovu
preciznih instrukcija.

---

 Korak 1 — Definisanje konteksta projekta (CLAUDE.md)

 Kreiranje CLAUDE.md fajla

Prva i najvaznija stvar bila je pisanje CLAUDE.md fajla u root direktorijumu projekta.
Ovaj fajl sluzi kao trajni kontekst koji Claude cita na pocetku svake sesije, slicno
kao onboarding dokument za novog programera.

 CLAUDE.md je sadrzao

- Opis projekta i cilj aplikacije
- Specifikaciju svih kolona dataseta
- Zahtjeve za GUI (boje, grid raspored, font)
- Pravila validacije za svako polje
- Strukturu koda (koje klase i metode ocekujemo)
- Eksplicitna zabranjena pravila (`NIKADA pack(), UVIJEK grid()`)

Claude Code automatski ucitava CLAUDE.md i koristi ga kao "system prompt" za cijeli
projekat. Ovo eliminise potrebu da svaki put ponavljate iste instrukcije i osigurava
konzistentnost kroz vise sesija.



Korak 2 — Analiza dataseta prije pisanja koda

Dobra praksa: Agent samostalno istrazuje codebase**

Umjesto da rucno opisujemo dataset, instruirali smo Claudea da sam procita CSV fajl
i analizira strukturu podataka. Claude je koristio alate (`Read`, `Glob`) da:

1. Pronadje CSV fajl u direktorijumu
2. Procita zaglavlje i prvih nekoliko redova
3. Ustanovi stvarne kolone (zdravstveni atributi, ne akademski)
4. Prilagodi plan implementacije stvarnim podacima

Ovo je bila kriticna faza jer je originalni dataset imao drugacije kolone od onih
opisanih u `CLAUDE.md` — Claude je to otkrio sam i prilagodio implementaciju.


 Korak 3 — Iterativni razvoj (nije sve odjednom)

 Inkrementalne izmjene, jedna stvar po sesiji

Aplikacija nije nastala u jednom koraku. Koristili smo iterativni pristup gdje se
svaka sesija fokusira na konkretan zadatak:

 Iteracija | Sta je implementirano |
|
| 1  Osnovna struktura: CRUD, Treeview, tamna tema, grid raspored |
| 2  Popravka fullscreen buga — stats+buttons u jedan panel |
| 3  Zaokruzivanje decimalnih vrijednosti (Height, Weight, BMI → int) |
| 4  Temperatura kao cijeli broj; poseban prozor za dodane studente |
| 5  Promjena dataseta na akademske atribute, pa povratak na zdravstvene |
| 6  Generisanje 500 studenata; krvna grupa sa +/- oznakom |
| 7  Brisanje iz liste dodanih; polje za svrhu liste; uklanjanje podnaslova |

Svaka iteracija je bila ''jedna precizna instrukcija'' — ne "uradi sve", nego tacno
sta treba promijeniti i zasto.

---

 Korak 4 — Precizne instrukcije (prompt engineering)



Umjesto: *"Popravi aplikaciju"*

Koristili smo: *"Temperatura treba biti cijeli broj, visina i tezina kao int, i prozor
u fullscreenu ne prikazuje dugmad"*

Claude Code reaguje bolje na instrukcije koje:
- Imenuju tacno koji element treba promijeniti
- Opisuju ocekivano ponasanje
- Navode ogranicenja (npr. "ne mijenjaj CSV")


 Korak 5 — Automatski backup podataka


U metodi `save_data()` implementirali smo automatski backup:

```python
def save_data(self):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if os.path.exists(CSV_FILE):
        shutil.copy2(CSV_FILE, os.path.join(BACKUP_DIR, f"backup_{ts}.csv"))
    # ... zatim pisanje novog fajla
```

Svaka izmjena kreira vremenski oznacen backup u `backups/` folderu.
CSV fajl se **nikada ne brise**, samo mijenja — sto je eksplicitno navedeno u `CLAUDE.md`.

---

 Korak 6 — Struktura koda po dobrim praksama

**Dobra praksa: Klasa, zasebne metode, konstante na vrhu**

Kod je organizovan prema standardima navedenim u `CLAUDE.md`:

```
app.py
├── Konstante boja (BG_COLOR, ACCENT_COLOR, ...)
├── class MedicalStudentApp(tk.Tk)
│   ├── CSV metode: load_data, save_data, add_student,
│   │               update_student, delete_student, search_students
│   └── GUI metode: create_header, create_search_bar, create_form,
│                   create_table, create_statistics, create_buttons,
│                   refresh_table, populate_form, clear_form
└── class AddedStudentsWindow(tk.Toplevel)
```

- Bez globalnih varijabli — sve je atribut klase (`self.data`, `self.filter_var`...)
-*Bez komentara koji opisuju sta kod radi — metode su dovoljno jasno nazvane
- Docstring na svakoj metodi — opisuje **zasto**, ne **sta**

---

 Korak 7 — Generisanje testnih podataka

 Skriptovano generisanje podataka, ne rucni unos

Umjesto rucnog popunjavanja CSV-a, napisali smo Python skriptu (inline, kroz Claude)
koja je generisala **500 realnih testnih studenata** sa:

- Randomizovanim ali validnim vrijednostima (Age 18-40, Height 150-200cm itd.)
- Svim vrijednostima kao cijeli brojevi
- Krvnom grupom sa +/- oznakom (A+, A-, B+, B-, AB+, AB-, O+, O-)
- Automatski izracunatim BMI iz visine i tezine

---

### Rezultat: Finalna arhitektura aplikacije

```
projekat/
├── app.py                      # Glavna aplikacija (~650 linija)
├── medical_students_dataset.csv # 500 studenata, 13 kolona
├── data.csv                    # Alternativni akademski dataset
├── CLAUDE.md                   # Kontekst projekta za Claude Code
├── README.md                   # Ovaj fajl
├── .gitignore                  # Ignorise __pycache__, backups/
└── backups/                    # Automatski backupi prije svake izmjene
```

---

Funkcionalnosti aplikacije

| Akcija | Kako koristiti |
|--------|---------------|
| **Pregled podataka** | Tabela se ucitava automatski pri pokretanju |
| **Pretraga** | Ukucajte ID, pol ili krvnu grupu u polje "Pretraga" |
| **Filter** | Odaberite kategoriju (Pol, Krvna grupa, Dijabetes, Pusenje) pa vrijednost |
| **Reset** | Dugme Reset brise pretragu i prikazuje sve zapise |
| **Dodaj studenta** | Popunite formu → kliknite "+ Dodaj studenta" |
| **Azuriraj** | Kliknite red u tabeli → izmijenite formu → "Azuriraj" |
| **Obrisi** | Kliknite red u tabeli → "Obrisi" → potvrdite dijalog |
| **Ocisti formu** | Resetuje sva polja i ponistava selekciju |
| **Lista dodanih** | Otvara poseban prozor sa studentima dodatim u sesiji |



 Kolone dataseta

| Kolona | Tip | Opis |
|--------|-----|------|
| Student ID | auto int | Automatski generisan jedinstveni identifikator |
| Age | int 18-40 | Starost studenta |
| Gender | Male/Female | Pol |
| Height | int (cm) | Visina |
| Weight | int (kg) | Tezina |
| Blood Type | A+/A-/B+/B-/AB+/AB-/O+/O- | Krvna grupa sa Rh faktorom |
| BMI | int (auto) | Automatski izracunat iz visine i tezine |
| Temperature | int (°F) | Temperatura tijela |
| Heart Rate | int (bpm) | Otkucaji srca |
| Blood Pressure | int (mmHg) | Krvni pritisak |
| Cholesterol | int (mg/dL) | Holesterol |
| Diabetes | Yes/No | Dijabetes |
 Smoking | Yes/No | Pusenje |







