.Treba mi kompletna Phyton
aplikacija za upravljanje podacima medicinskih studenata.

Tvoja uloga
Ponašaj se kao autonomni coding agent. Prije pisanja koda:
1. Analiziraj postojeći data.csv fajl u ovom direktorijumu
2. Napravi detaljan plan šta ćeš izgraditi
3. Sačekaj moje odobrenje prije nego nastaviš

 Kolone dataseta (data.csv)
Prilozene u Medical students.csv


 GUI - samo Tkinter
- Koristi grid raspored za SVE elemente, 
  nikako pack() ili place()
- Tamna medicinska tema:
- Naslov prozora: "Medical Students Management System"
- Minimalna veličina prozora: 1200x700

 Struktura rasporeda (grid)
- Red 0: naslov koji se proteže cijelom širinom
- Red 1: search bar i filter dropdown
- Red 2 (lijeva kolona): forma za unos sa svim poljima
- Red 2 (desna kolona): Treeview tabela sa scrollbarom
- Red 3: statistike (ukupno studenata, prosječni GPA,
  prosječni MCAT, prosječni Exam Score)
- Red 4: dugmad za akcije (Dodaj, Ažuriraj, Obriši, Očisti)

### CRUD operacije
1. DODAJ: validiraj sva polja, automatski generiši 
   StudentID, dodaj u CSV, osvježi tabelu
2. PRIKAŽI: učitaj sve podatke pri pokretanju, 
   prikaži u Treeview tabeli
3. AŽURIRAJ: klikni red da popuniš formu, izmijeni 
   polja, klikni Ažuriraj da sačuvaš promjene u CSV
4. OBRIŠI: klikni red, dijalog za potvrdu, 
   ukloni iz CSV, osvježi tabelu

### Pravila validacije
- Age: cijeli broj između 18-40
- GPA: decimalni broj između 0.0-4.0
- MCAT Score: cijeli broj između 472-528
- Exam Score: decimalni broj između 0-100
- Publication Count: cijeli broj >= 0
- Prazna polja nisu dozvoljena
- Prikaži crvenu poruku greške ispod forme 
  pri neispravnom unosu
- Prikaži zelenu poruku uspjeha pri uspješnoj operaciji

### Pretraga i filtriranje
- Pretraga po nazivu univerziteta u realnom vremenu
- Filter dropdown po: Sve, Godina, Pol, 
  Kliničko iskustvo, Istraživačko iskustvo
- Dugme Reset za brisanje pretrage i prikaz svih zapisa

### Zahtjevi strukture koda
- Klasa: MedicalStudentApp(tk.Tk)
- Zasebne metode za CSV operacije:
  * load_data()
  * save_data()
  * add_student()
  * update_student()
  * delete_student()
  * search_students()
- Zasebne metode za GUI:
  * create_header()
  * create_search_bar()
  * create_form()
  * create_table()
  * create_statistics()
  * create_buttons()
  * refresh_table()
  * populate_form()
  * clear_form()
- Svaka metoda mora imati docstring
- Konstante boja definisane na vrhu fajla
- Bez globalnih varijabli, koristiti atribute klase

## Fajlovi za kreiranje
1. app.py - glavna aplikacija
2. CLAUDE.md - kontekst projekta i coding standardi
3. README.md - uputstvo za pokretanje i korištenje

#adržaj CLAUDE.md
Uključi:
- Opis projekta
- Kako pokrenuti aplikaciju
- Korišteni coding standardi
- Opis dataseta
- Pravila grid rasporeda



Važna pravila
- NIKADA ne koristiti pack() ili place() za raspored
- UVIJEK koristiti grid() za svaki widget
- CSV fajl se nikada ne smije obrisati, samo mijenjati
- Uvijek napravi backup prije mijenjanja CSV-a
- Obraditi FileNotFoundError za slučaj da CSV ne postoji
- Koristiti utf-8 enkodiranje za CSV operacije

Počni čitanjem data.csv fajla, zatim predstavi 
plan implementacije. Ne piši nikakav kod dok 
ne odobrim plan.
