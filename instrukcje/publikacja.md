# Instrukcja: publikacja posta dnia (wtorek / środa / czwartek)

Działasz bez nadzoru. Publikujesz post dnia (oraz ewentualne zaległe posty – sekcja 1a) na Instagramie i Facebooku Couch & Coach przez narzędzia Windsor.ai for Social Media. Nie zadawaj pytań.

Baza adresów: `https://raw.githubusercontent.com/CouchAndCoach/couch-and-coach-posts/main`

## 1. Ustal post dnia
- DZIŚ = dzisiejsza data w strefie Europe/Warsaw. WTOREK = wtorek bieżącego tygodnia (dziś, jeśli dziś wtorek; dziś−1 w środę; dziś−2 w czwartek).
- Pobierz `BAZA/dane/WTOREK.json` (curl -sS lub WebFetch). Wybierz obiekt z `"date"` równym DZIŚ.
- Jeśli pliku nie ma albo brak posta na dziś → nic nie publikuj, wyślij push „Brak posta na dziś (DZIŚ) – nic nie opublikowano.” i zakończ.

## 1a. Zaległe posty – Ty pilnujesz kolejności w mozaice (zasada Szymona od 25.11.2026)
Kolejność publikacji w siatce musi zostać zachowana: wtorek → środa → czwartek, tydzień po tygodniu. Zarządzasz tym samodzielnie, bez pytania.
- Sprawdź posty zaplanowane PRZED dzisiejszym: w bieżącym tygodniu (`dane/WTOREK.json`) oraz w poprzednim (`dane/<WTOREK−7>.json`, jeśli istnieje).
- Post uznajesz za opublikowany, jeśli istnieje `posty/<jego wtorek>/opublikowano_<jego data>.txt`. Jeśli pliku nie ma, ZANIM uznasz post za zaległy, sprawdź w Windsor (`get_data`, connector instagram, ostatnie 14 dni – najpierw `get_fields`), czy na Instagramie nie ma już posta z tym samym początkiem opisu. Jeśli jest – post wyszedł (dopisz brakujący plik śladu w kroku 4) i NIE publikuj go ponownie. Jeśli nie da się tego sprawdzić, nie publikuj zaległego posta i opisz to w wyniku.
- Tydzień z plikiem STOP pomijasz (to decyzja Szymona) i zaznaczasz w wyniku, że siatka może być przesunięta.
- Zaległe posty publikujesz w tym samym przebiegu, w kolejności chronologicznej, PRZED postem dnia (bezpieczniki z sekcji 2 i kroki z sekcji 3 dotyczą każdego z nich, obrazy z folderu jego tygodnia).
- Jeśli opis zaległego posta odnosi się do terminu, który już minął (np. „Black Friday w ten piątek” po piątku), popraw tylko to odniesienie czasowe w pierwszym zdaniu, resztę zostaw bez zmian. Poprawiony tekst podaj w wyniku.
- Jeśli zaległego posta nie uda się opublikować, NIE publikuj kolejnych (także posta dnia) – kolejność jest ważniejsza niż termin. Wyślij push z opisem i zakończ; kolejny przebieg spróbuje ponownie.

## 2. Bezpieczniki
- `BAZA/posty/WTOREK/STOP` zwraca 200 → nic nie publikuj, push „Publikacja wstrzymana (STOP).” i zakończ.
- Zatwierdzenie NIE jest wymagane (zasada Szymona od 25.11.2026): jeśli nie ma pliku STOP, publikujesz. Plik `ZATWIERDZONE` nie ma już znaczenia – nie sprawdzaj go.
- Uwaga: plik STOP dodany na GitHubie może pojawić się na raw.githubusercontent.com z kilkuminutowym opóźnieniem – jeśli STOP zwraca 404, odczekaj 2 minuty i sprawdź jeszcze raz przed publikacją.
- `BAZA/posty/WTOREK/opublikowano_DZIŚ.txt` zwraca 200 → już opublikowano, zakończ bez publikacji.
- Sprawdź curl -sI, że oba obrazy zwracają 200 i `image/jpeg`:
  `BAZA/posty/WTOREK/<name>_slajd1.jpg`, `BAZA/posty/WTOREK/<name>_slajd2.jpg`.

## 3. Publikacja
Narzędzia Windsor (jeśli są odroczone, załaduj przez ToolSearch: "select:mcp__Windsor_ai_for_Social_Media__get_connectors,mcp__Windsor_ai_for_Social_Media__execute_action").
1. `get_connectors` (include_actions false) → konta: instagram (couch_and_coach), facebook_organic (Couch & Coach). Użyj ID kont z wyniku.
2. Instagram: `execute_action` connector "instagram", action "create_carousel_post", params `{"image_urls": [slajd1, slajd2], "caption": captions.instagram}`.
3. Facebook: `execute_action` connector "facebook_organic", action "create_photo_post", params `{"image_url": slajd1, "caption": captions.facebook}`.
Każdą akcję wykonaj RAZ. Jeśli zwróci błąd, nie ponawiaj więcej niż jeden raz i tylko gdy błąd jest przejściowy (timeout, 5xx); przy błędzie walidacji nie ponawiaj.

## 4. Ślad (ważne – od niego zależy wykrywanie zaległych postów)
Jeśli masz dostęp do repozytorium (narzędzie add_repo z access "push" dla CouchAndCoach/couch-and-coach-posts działa), dodaj plik `posty/WTOREK/opublikowano_DZIŚ.txt` z wynikiem (ID postów) i wypchnij. Jeśli nie – pomiń.

## 5. Powiadomienie
Push (PushNotification, status "proactive", jedna linia do 200 znaków):
- sukces: „Opublikowano: [hasło] (IG ✔, FB ✔). LinkedIn i X: wklej opis ręcznie.” (przy zaległych: „Opublikowano zaległy [hasło] + [hasło dnia] …”)
- częściowo/błąd: „Publikacja [hasło]: IG [✔/✘], FB [✔/✘] – szczegóły w wyniku zadania.”
Końcowa odpowiedź: co opublikowano, ID postów lub treść błędów, a do ręcznego wklejenia opisy `captions.linkedin` i `captions.x`.
