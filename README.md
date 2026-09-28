# Alla städer — handelsresandeproblemet i klassrummet

En interaktiv demonstration i Python för elever i åldern 14–15 år. Välj en rutt,
upptäck hur snabbt antalet möjligheter växer och se datorn ta bort omvägar.

## Starta programmet

Öppna PowerShell i `C:\Dev\Python\TSPDemo` och kör:

```powershell
.\.venv\Scripts\python.exe run_demo.py
```

Vid behov installeras beroendena med:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Maximera fönstret eller tryck **F** för helskärm. En skärm med minst
1 600 × 900 bildpunkter rekommenderas för projektion.

Programmet kräver Python 3.10 eller senare och ett grafiskt Matplotlib-gränssnitt,
exempelvis Tk som ingår i standardinstallationen av Python för Windows.
Projektets befintliga virtuella miljö har reparerats med Codex Python 3.12.
Skapa en ny `.venv` med den lokala Python-installationen om projektet flyttas
till en annan dator.

## Presentationsläge — som ett bildspel

```powershell
.\.venv\Scripts\python.exe run_demo.py --mode presentation --fullscreen
```

Här finns inga knappar eller någon tangentbordslathund på skärmen. **Mellanslag**, **högerpil**, **Enter** eller **Page Down**
går vidare. **Vänsterpil** eller **Page Up** går tillbaka till föregående steg.
**F** växlar helskärm. **Home** börjar om från 5 städer.

- **5 städer:** klicka på städerna i publikens ordning. Tryck sedan på mellanslag
  för att visa datorns kortaste rutt och jämföra med publikens sträcka.
- Nästa tryck visar **10 städer** där ni gör samma sak.
- Nästa tryck visar **20 städer** utan rutt. Ett tryck till visar datorns
  **första förslag**, som ligger still så länge ni vill. Ytterligare ett tryck
  startar förbättringen av just den rutten. Resultatet ligger kvar tills ni går vidare.
- Upprepa med **100** och **1 000 städer**. Det sista resultatet ligger kvar.

**Backsteg** ångrar den senast valda staden, även när publikens rutt är komplett.
Alla städer måste väljas innan jämförelsen kan visas. Under en förbättring
ignoreras extra framåttryckningar så att resultatet inte hoppas över.
Det går att backa eller börja om även under animationen. Publikens rutt bevaras
när ni backar från jämförelsen. Från en pågående eller färdig förbättring
backar ni till det oförändrade första förslaget. Beräkningstiden är dold i presentationsläget.

Presentationen börjar alltid med 5 städer; `--cities` gäller bara det fria läget.
`--seed` fungerar i båda lägena utan att visas på skärmen.

Det tidigare läget med alla knappar finns kvar:

```powershell
.\.venv\Scripts\python.exe run_demo.py --mode interactive
```

Utan `--mode` startas det fria läget som tidigare.

## Förslag på lektionsupplägg (fritt läge)

1. Börja med **5 städer**. Låt eleverna gissa vilken rutt som är kortast.
2. Tryck på **Publiken** och klicka på städerna i den ordning eleverna föreslår.
   Den sista förbindelsen går automatiskt tillbaka till starten. Upprepade klick
   på samma stad ignoreras. **Nollställ rutt** börjar om. Publikläget stöder 5 och 10 städer.
3. Tryck på **Lös**. Den exakt kortaste rutten visas och publikens sträcka finns
   kvar för jämförelse. Avstånden mäts fågelvägen i godtyckliga enheter.
4. Upprepa med **10 städer**. Antalet möjliga rutter ökar från 12 till 181 440.
5. Välj **20**, **100** och **1 000 städer**. Låt eleverna titta på kartan och
   tryck sedan på **Lös** för att skapa en första rutt med närmaste granne.
6. Tryck på **Förbättra** och se hur rutten blir kortare. **Kör demo** skapar
   en ny rutt med närmaste granne och visar förbättringen automatiskt för den
   valda storleken. Knappen ändrar inte antalet städer.
7. Procenttalet jämför aktuell sträcka med den första rutten. **Lös** och
   **Kör demo** ger ett nytt jämförelsevärde. **Förbättra** kan användas igen.

Optimering innebär att hitta det bästa alternativet bland många möjligheter.
Även en snabb dator kan inte prova alla rutter när städerna blir många.
En heuristik gör smarta val snabbt, men bevisar inte att svaret är det allra bästa.

Sophämtning är ett vardagligt exempel: en sopbil besöker många platser.
I verkligheten tillkommer flera bilar, kapacitetsgränser, tidskrav, enkelriktade
gator, trafik och återresor till depån. Dessa villkor ingår inte i demonstrationen.

## Algoritmer och begränsningar

| Antal städer | Lös | Förbättra / Kör demo |
|---|---|---|
| 5, 10 | Exakt lösning med Held–Karp | Kör demo börjar med närmaste granne, sedan 2-opt |
| 20, 100, 1 000 | Närmaste granne från stad 1 | Lokal sökning med 2-opt |

Held–Karp använder dynamisk programmering: den sparar den kortaste vägen för
varje besökt delmängd och slutstad. Tidsåtgången växer som O(n² 2ⁿ), och metoden
är därför begränsad till högst 10 städer. Närmaste granne väljer upprepade gånger
den närmaste obesökta staden. 2-opt vänder en del av rutten om två nya förbindelser
ger en kortare total sträcka.

2-opt gör högst 12 genomgångar och använder högst tre sekunders beräkningstid
i det interaktiva programmet. Arbetet delas upp i ungefär 12 ms långa delar.
För 1 000 städer visas högst tre ändringar per uppdatering med 60 ms mellanrum.
Mindre exempel visar en ändring per 180 ms. En inledande paus på 800 ms gör
det möjligt att se den första rutten innan förbättringen börjar.

Ritning och animationspauser ingår inte i den visade beräkningstiden, så den
verkliga väntetiden kan vara längre. Knapparna fungerar under animationen.
Byte av storlek eller nollställning avbryter den. Sökningen kan stanna innan
ett lokalt optimum uppnåtts, och ett lokalt optimum behöver inte vara globalt.
En exakt lösning för ett litet exempel går vanligtvis inte att förbättra mer.

Avstånden lagras i en NumPy-matris med O(n²) element, ungefär 8 MB för 1 000 städer.
Antalet rutter är (n−1)! / 2 när starten är fixerad och de två färdriktningarna
räknas som samma rutt. Stora antal beräknas med log-gamma i stället för enorma
heltal. För 1 000 städer är antalet ungefär 2,01 × 10²⁵⁶⁴.

## Presentationsbilder

**Spara PNG** sparar en ren bild utan knappar i `output/`. Filnamnet innehåller
antal städer, lösningssteg och tidsstämpel.

Skapa hela uppsättningen presentationsbilder med:

```powershell
.\.venv\Scripts\python.exe generate_images.py
```

Kommandot skapar **17 PNG-bilder med 2 880 × 1 620 bildpunkter**: enbart städer,
första rutten med närmaste granne och förbättrad rutt med 2-opt för varje storlek,
samt exakta lösningar för 5 och 10 städer. Bilderna har svenska texter.
Exporten använder 12 genomgångar utan tidsgräns för att ge samma resultat varje gång.
Variabla beräkningstider utelämnas. En ny körning skriver över samma filnamn.
Den interaktiva, tidsbegränsade lösningen kan skilja sig något.

## Reproducerbara exempel

Standardexemplet använder slumpfrö 42. Prova 7 och 2026 för alternativa kartor:

```powershell
.\.venv\Scripts\python.exe run_demo.py --seed 7 --cities 100
.\.venv\Scripts\python.exe generate_images.py --seed 2026 --output output_alternativ
```

Slumpfröet visas inte i gränssnittet eller på bilderna. **Slumpa nya städer**
ökar slumpfröet med ett. Byte av antal städer behåller det aktuella värdet,
så att samma exempel går att återvända till. Batchbildernas tekniska filnamn
behåller slumpfröet för att skilja olika uppsättningar åt.

## Filer och tester

- `run_demo.py`: startar det interaktiva programmet.
- `generate_images.py`: skapar reproducerbara presentationsbilder.
- `tsp_demo/presentation.py`: stegvis presentation och tangentbordsstyrning.
- `tsp_demo/app.py`: knappar, publikläge och animation.
- `tsp_demo/algorithms.py`: Held–Karp, närmaste granne och stegvis 2-opt.
- `tsp_demo/model.py`: städer, avstånd, talformatering och antal rutter.
- `tsp_demo/plotting.py`: gemensam utformning och bildexport.
- `tests/test_demo.py`: kontroller av algoritmer och arbetsflöden.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Testerna jämför exakta lösningar med uttömmande sökning för sju städer,
kontrollerar giltiga rutter och förbättringar, provar alla storlekar och avbruten
animation samt testar publikens inmatning, jämförelse och bildexport.
