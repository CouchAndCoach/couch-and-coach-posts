# Instrukcja: publikacja posta dnia (wtorek / środa / czwartek)

Działasz bez nadzoru. Publikujesz JEDEN post dnia na Instagramie i Facebooku Couch & Coach przez narzędzia Windsor.ai for Social Media. Nie zadawaj pytań.

Baza adresów: `https://raw.githubusercontent.com/CouchAndCoach/couch-and-coach-posts/main`

## 1. Ustal post dnia
- DZIŚ = dzisiejsza data w strefie Europe/Warsaw. WTOREK = wtorek bieżącego tygodnia (dziś, jeśli dziś wtorek; dziś−1 w środę; dziś−2 w czwartek).
- Pobierz `BAZA/dane/WTOREK.json` (curl -sS lub WebFetch). Wybierz obiekt z `"date"` równym DZIŚ.
- Jeśli pliku nie ma albo brak posta na dziś → nic nie publikuj, wyślij push „Brak posta na dziś (DZIŚ) – nic nie opublikowano.” i zakończ.

## 2. Bezpieczniki
- `BAZA/posty/WTOREK/STOP` zwraca 200 → nic nie publikuj, push „Publikacja wstrzymana (STOP).” i zakończ.
- `BAZA/posty/WTOREK/ZATWIERDZONE` NIE zwraca 200 → nic nie publikuj, push „Post na dziś czeka na zatwierdzenie – napisz w projekcie »publikuj«.” i zakończ.
- `BAZA/posty/WTOREK/opublikowano_DZIŚ.txt` zwraca 200 → już opublikowano, zakończ bez publikacji.
- Sprawdź curl -sI, że oba obrazy zwracają 200 i `image/jpeg`:
  `BAZA/posty/WTOREK/<name>_slajd1.jpg`, `BAZA/posty/WTOREK/<name>_slajd2.jpg`.

## 3. Publikacja
Narzędzia Windsor (jeśli są odroczone, załaduj przez ToolSearch: "select:mcp__Windsor_ai_for_Social_Media__get_connectors,mcp__Windsor_ai_for_Social_Media__execute_action").
1. `get_connectors` (include_actions false) → konta: instagram (couch_and_coach), facebook_organic (Couch & Coach). Użyj ID kont z wyniku.
2. Instagram: `execute_action` connector "instagram", action "create_carousel_post", params `{"image_urls": [slajd1, slajd2], "caption": captions.instagram}`.
3. Facebook: `execute_action` connector "facebook_organic", action "create_photo_post", params `{"image_url": slajd1, "caption": captions.facebook}`.
Każdą akcję wykonaj RAZ. Jeśli zwróci błąd, nie ponawiaj więcej niż jeden raz i tylko gdy błąd jest przejściowy (timeout, 5xx); przy błędzie walidacji nie ponawiaj.

## 4. Ślad (opcjonalnie)
Jeśli masz dostęp do repozytorium (narzędzie add_repo z access "push" dla CouchAndCoach/couch-and-coach-posts działa), dodaj plik `posty/WTOREK/opublikowano_DZIŚ.txt` z wynikiem (ID postów) i wypchnij. Jeśli nie – pomiń.

## 5. Powiadomienie
Push (PushNotification, status "proactive", jedna linia do 200 znaków):
- sukces: „Opublikowano: [hasło] (IG ✔, FB ✔). LinkedIn i X: wklej opis ręcznie.”
- częściowo/błąd: „Publikacja [hasło]: IG [✔/✘], FB [✔/✘] – szczegóły w wyniku zadania.”
Końcowa odpowiedź: co opublikowano, ID postów lub treść błędów, a do ręcznego wklejenia opisy `captions.linkedin` i `captions.x`.
