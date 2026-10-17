# Major Incident Board

## Hallgató

**Nádasi Richárd** (monogram: NR)
Neptun-kód: **JO4N9J**
Szkript nyelvek – Python, projektfeladat

## Feladat leírása

Az alkalmazás egy IT-üzemeltetési **Major Incident Board**, vagyis egy kiemelt incidenseket kezelő irányítópult, grafikus felülettel (tkinter).

- Új incidens nyitható leírással, érintett szolgáltatással és prioritással (P1–P4).
- A **Szimulált riasztás** gomb (F5) véletlenszerű monitoring-riasztásból hoz létre incidenst.
- Az incidensek listája prioritás szerint színezett. A nyitott incidensek időtartama másodpercenként frissül.
- Kiválasztott incidensnél látszik az idővonal. Új bejegyzés vehető fel (dupla kattintással is), és módosítható a státusz (Nyitott / Vizsgálat alatt / Elhárítva).
- Aktív P1 incidens esetén a fejléc pirosra vált.
- Alul oszlopdiagram mutatja a nyitott incidenseket prioritás szerint, alatta pedig a statisztika: MTTR (átlagos helyreállítási idő) átlag, medián, szórás és a leggyakrabban érintett szolgáltatás.
- Az adatok JSON fájlba mentődnek (`incidents.json`), és újraindításkor visszatöltődnek.

## Indítás

```
python3 main.py
```

Csak a Python standard könyvtárát használja, külön telepítés nem kell. Python 3.10 vagy újabb, tkinter támogatással.

## Program felépítése

| Fájl | Szerep |
|---|---|
| `main.py` | Indítás, itt jön létre a `root` alapablak és az `app` program |
| `nr_board.py` | Saját modul: a grafikus felület (`NRIncidentBoard` osztály) |
| `nr_incident.py` | Saját modul: az incidens adatmodellje és a segédfüggvények |

## Modulok és a használt függvények

### Tanult modulok

- **tkinter** (grafikai modul): `Tk`, `Frame`, `Label`, `Canvas`, `Text`, `StringVar`, `bind`, `after`, `protocol`, `bell`.
  - `tkinter.ttk`: `Treeview`, `Combobox`, `Button`, `Entry`, `LabelFrame`, `Scrollbar`, `Style`.
  - `tkinter.messagebox`: `showwarning`, `showinfo`.
  - `tkinter.simpledialog`: `askstring`.
- **random**: `choice`, `choices`, `randint`, a szimulált riasztásokhoz.
- **datetime**: `datetime.now`, `strftime`, `strptime`, `timedelta`.

### Bemutatandó modul: `statistics`

Az incidensek helyreállítási idejéből (MTTR) számol:

- `statistics.mean()` – átlagos helyreállítási idő
- `statistics.median()` – medián helyreállítási idő
- `statistics.pstdev()` – a helyreállítási idők szórása
- `statistics.mode()` – a leggyakrabban érintett szolgáltatás

### Egyéb modulok

- **json**: `dump`, `load`, mentés és betöltés (fájlkezelés).
- **pathlib**: `Path`, az adatfájl elérési útja.

### Saját modulok és függvények

**`nr_incident.py`**

- `nr_format_duration(minutes)` – percet „X ó YY p” formára alakít
- `nr_priority_color(priority, light=False)` – a prioritáshoz tartozó színt adja vissza
- `nr_random_incident(number)` – véletlenszerű szimulált incidenst hoz létre
- `nr_statistics(incidents)` – MTTR statisztikát számol a `statistics` modullal
- `nr_save_incidents(path, incidents)` – JSON fájlba ment
- `nr_load_incidents(path)` – JSON fájlból tölt be

**`nr_board.py`** – a felület, lásd az `NRIncidentBoard` osztályt.

## Osztályok

### `NRIncident` (`nr_incident.py`)

Egy incidenst ír le: azonosító, leírás, szolgáltatás, prioritás, státusz, nyitás és elhárítás ideje, idővonal.
Metódusok: `code`, `is_open()`, `add_update()`, `set_status()`, `duration_minutes()`, `to_dict()`, `from_dict()`.

### `NRIncidentBoard` (`nr_board.py`)

A `tk.Frame`-ből származó grafikus felület.
Fő metódusok: `create_incident()`, `simulate_alert()`, `change_status()`, `add_update()`, `refresh()`, `draw_chart()`, `update_stats()`, `tick()`, `on_close()`.

## Eseménykezelés

| Esemény | Hatás |
|---|---|
| Gombnyomások (`command=`) | Megnyitás, szimulált riasztás, státusz beállítása, bejegyzés |
| `<<TreeviewSelect>>` | Kiválasztott incidens részleteinek megjelenítése |
| `<Double-1>` | Dupla kattintás a sorra: új bejegyzés |
| `<Return>` a leírás mezőben | Incidens megnyitása |
| `<Control-n>` | Ugrás a leírás mezőre |
| `<F5>` | Szimulált riasztás |
| `<Configure>` a Canvason | Diagram újrarajzolása átméretezéskor |
| `after(1000, ...)` | Óra és időtartamok frissítése másodpercenként |
| `WM_DELETE_WINDOW` | Mentés az ablak bezárásakor |
