# Couch & Coach – posty słownikowe

Repozytorium robocze do automatycznych postów Couch & Coach na Instagram i Facebook.
Grafiki muszą mieć publiczny adres URL, bo Instagram (przez Windsor.ai) pobiera je z internetu.

## Struktura

- `generator/render.py` – generator grafik (mozaika A–F, slajd 1 + slajd 2, 1080×1350 JPG)
- `generator/fonts/` – fonty (Archivo Black, Poppins SemiBold, Open Sans; licencja SIL OFL)
- `generator/assets/logo.png` – logo Couch & Coach (prawa zastrzeżone, nie do ponownego użycia)
- `dane/RRRR-MM-DD.json` – treść postów na tydzień (data wtorku)
- `posty/RRRR-MM-DD/` – gotowe grafiki na tydzień

## Użycie

```
pip install pillow
python3 generator/render.py dane/2026-11-17.json posty/2026-11-17
```

Nazwy plików mają numer w kolejności publikacji, np. `1_wtorek_F_..._slajd1.jpg`.

## Pozycje w siatce

| Poz. | Typ | Tło |
|---|---|---|
| A | DID YOU KNOW? | beżowy |
| B | IDIOM OF THE DAY | terakota |
| C | IDIOM OF THE DAY | czarny |
| D | QUOTE OF THE DAY | szary |
| E | WORD OF THE DAY | szary |
| F | WORD OF THE DAY | terakota |

Tydzień 1 cyklu: wtorek F → środa E → czwartek D. Tydzień 2: wtorek C → środa B → czwartek A.

© Couch & Coach. Wszystkie prawa zastrzeżone (poza fontami na licencji OFL).
