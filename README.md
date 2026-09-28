# Travelling Salesman Problem (TSP)

## Starta

**Presentationsläge utan knappar, i helskärm:**

```powershell
.\.venv\Scripts\python.exe run_demo.py --mode presentation --fullscreen
```

**Fritt läge med alla knappar:**

```powershell
.\.venv\Scripts\python.exe run_demo.py --mode interactive
```

Utan argument startas det fria läget med 5 städer.

## Presentationsläge

Ordning: **5 → 10 → 20 → 100 → 1 000 städer**.

- **5 och 10:** klicka på varje stad i önskad ordning. Gå vidare för att visa datorns kortaste rutt. Gå vidare igen för nästa storlek.
- **20, 100 och 1 000:** städer utan rutt → första förslaget → animerad förbättring → nästa storlek. Varje pil motsvarar ett knapptryck. Första förslaget och resultatet ligger kvar tills du går vidare.
- Efter 1 000 städer ligger slutresultatet kvar.

| Tangent / klick | Funktion |
|---|---|
| Mellanslag, →, Enter eller Page Down | Nästa steg. Alla städer måste vara valda i publikläget. Ignoreras medan förbättringen körs. |
| ← eller Page Up | Föregående steg. Avbryter eventuell förbättring och återställer föregående rutt. |
| Klick på en stad | Lägg till staden i publikens rutt för 5 eller 10 städer. |
| Backsteg | Ångra senaste stadsvalet i publikläget, även när rutten är komplett. |
| Home | Börja om från 5 städer. |
| F | Växla helskärm. |

## Fritt läge

| Knapp | Funktion |
|---|---|
| 5 / 10 / 20 / 100 / 1 000 städer | Byt antal städer och nollställ rutten. |
| Slumpa nya städer | Skapa en ny karta med samma antal städer. |
| Publiken | Välj en egen rutt genom att klicka på städerna. Endast 5 och 10 städer. |
| Lös | Visa den kortaste rutten för 5 och 10 städer, annars datorns första förslag. Publikens sträcka behålls för jämförelse. |
| Förbättra | Förbättra aktuell rutt. Skapar en rutt först om ingen finns. |
| Kör demo | Skapa ett nytt första förslag och starta förbättringen automatiskt. |
| Nollställ rutt | Ta bort rutten och jämförelsevärdena. Behåll städerna. |
| Spara PNG | Spara aktuell vy utan knappar. En påbörjad publikrutt måste först slutföras. |

**F** växlar helskärm. Byte av antal städer, ny karta eller nollställning avbryter en pågående förbättring.

## Argument till run_demo.py

| Argument | Värden | Standard | Funktion |
|---|---|---|---|
| `--mode` | `presentation`, `interactive` | `interactive` | Välj läge. |
| `--fullscreen` | Ingen parameter | Av | Starta i helskärm. |
| `--cities` | `5`, `10`, `20`, `100`, `1000` | `5` | Startstorlek i fritt läge. Ignoreras i presentationsläget, som alltid börjar med 5. |
| `--seed` | Icke-negativt heltal | `42` | Slumpfrö. Samma värde ger samma karta. Visas inte på skärmen. |
| `--output` | Sökväg | `output` | Mapp för Spara PNG i fritt läge. Relativa sökvägar utgår från aktuell arbetsmapp. |
| `-h`, `--help` | Ingen parameter | — | Visa kommandoradshjälp och avsluta. |

## Skapa presentationsbilder

```powershell
.\.venv\Scripts\python.exe generate_images.py
```

Skapar 17 PNG-bilder i `output/`, med upplösningen 2 880 × 1 620: städer, första rutt och förbättrad rutt för varje storlek samt exakta rutter för 5 och 10 städer. Befintliga filer med samma namn skrivs över.

| Argument | Standard | Funktion |
|---|---|---|
| `--seed` | `42` | Icke-negativt heltal för reproducerbara kartor. |
| `--output` | `output` | Mapp för bilderna. |
| `-h`, `--help` | — | Visa kommandoradshjälp och avsluta. |

## Installation och tester

Kräver Python 3.10 eller senare med Tk. På en ny dator, skapa miljön och installera beroendena:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Kör testerna:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
