# Dokumentacja - Gra Wilk i Owce

## Autor
**Jan Kowalski**

## Sformułowanie zadania
Implementacja sieciowej gry "Wilk i Owce" dla dwóch graczy z interfejsem graficznym. Gra wykorzystuje architekturę klient-serwer z komunikacją przez gniazda TCP.

### Zasady gry
- Plansza 8x8, pionki poruszają się po czarnych polach (po skosie)
- **Owce (4 sztuki)** - startują w górnym rzędzie, mogą poruszać się tylko w dół (po skosie o 1 pole)
- **Wilk (1 sztuka)** - startuje w dolnym rzędzie na losowym czarnym polu, może poruszać się w dowolnym kierunku po skosie o 1 pole
- **Wygrana wilka** - dotarcie do górnego rzędu (rząd 0)
- **Wygrana owiec** - zablokowanie wilka tak, że nie ma możliwego ruchu

---

## Schemat komunikacji

### Architektura
```
+--------+          TCP          +--------+
| Klient | <------------------> | Serwer |
| (WILK) |                      |        |
+--------+          TCP         +--------+
                                    ^
+--------+          TCP             |
| Klient | <------------------------+
| (OWCE) |
+--------+
```

- **Serwer** (`server.py`) - zarządza stanem gry, waliduje ruchy, rozsyła aktualizacje
- **Klienci** (`client.py`) - wyświetlają interfejs graficzny, wysyłają ruchy gracza

### Protokół komunikacji
- **Transport**: TCP (gniazda strumieniowe)
- **Format danych**: JSON
- **Separator wiadomości**: znak nowej linii `\n`
- **Adres**: localhost (127.0.0.1), port 65432

### Typy wiadomości

#### Serwer -> Klient

| Typ | Opis | Pola |
|-----|------|------|
| `INIT` | Inicjalizacja po połączeniu | `role` (WILK/OWCE), `board` (stan planszy) |
| `UPDATE` | Aktualizacja po ruchu | `board`, `turn`, opcjonalnie `winner` |
| `ERROR` | Błąd (np. nieprawidłowy ruch) | `msg` (treść błędu) |
| `EXIT` | Zamknięcie serwera | `msg` |

#### Klient -> Serwer

| Typ | Opis | Pola |
|-----|------|------|
| `MOVE` | Wykonanie ruchu | `from` [r, c], `to` [r, c] |

### Przykłady komunikatów

**INIT** (serwer -> klient):
```json
{"type": "INIT", "role": "WILK", "board": [[0,1,0,1,0,1,0,1], ...]}
```

**MOVE** (klient -> serwer):
```json
{"type": "MOVE", "from": [7, 2], "to": [6, 3]}
```

**UPDATE** (serwer -> klienci):
```json
{"type": "UPDATE", "board": [[...]], "turn": "OWCE"}
```

---

## Koordynacja procesów i wątków

### Serwer
- **Wątek główny** - akceptuje połączenia nowych klientów
- **Wątki obsługi klientów** - po jednym dla każdego gracza, nasłuchują ruchów
- **Synchronizacja** - `threading.Lock` chroni dostęp do stanu gry (`self.board`, `self.turn`)

### Klient
- **Wątek główny** - pętla GUI (pygame), obsługa zdarzeń myszy, renderowanie
- **Wątek sieciowy** (daemon) - odbiera wiadomości z serwera, wkłada je do kolejki
- **Synchronizacja** - `queue.Queue` (thread-safe) do przekazywania wiadomości między wątkami

### Schemat przepływu danych w kliencie
```
[Wątek sieciowy]              [Wątek GUI]
      |                            |
 recv(socket)                      |
      |                            |
 json.loads()                      |
      |                            |
 queue.put(msg) -----> queue.get() |
                            |      |
                    aktualizuj stan|
                            |      |
                    pygame.draw()  |
```

---

## Instrukcja użytkowania

### Wymagania
- Python 3.x
- Biblioteka pygame (`pip install pygame`)

### Uruchomienie

1. **Uruchom serwer**:
   ```
   python server.py
   ```
   Serwer wyświetli: `Serwer uruchomiony na 127.0.0.1:65432. Oczekiwanie na graczy...`

2. **Uruchom pierwszego klienta** (gracz WILK):
   ```
   python client.py
   ```

3. **Uruchom drugiego klienta** (gracz OWCE):
   ```
   python client.py
   ```

### Rozgrywka
- Kliknij na swój pionek aby go zaznaczyć (zielona ramka)
- Kliknij na docelowe pole aby wykonać ruch
- Na górze ekranu wyświetlany jest status (Twoja tura / Czekaj na przeciwnika)
- Gra kończy się gdy wilk dotrze do górnego rzędu lub zostanie zablokowany

### Obsługiwane sytuacje błędne

| Sytuacja | Obsługa |
|----------|---------|
| Ruch poza swoją turą | Serwer odrzuca, klient ignoruje kliknięcia |
| Nieprawidłowy ruch (zły kierunek, zajęte pole) | Serwer wysyła ERROR, ruch nie jest wykonany |
| Kliknięcie na pionek przeciwnika | Klient ignoruje (nie zaznacza) |
| Rozłączenie gracza | Serwer wypisuje błąd, gra zostaje przerwana |
| Zamknięcie serwera (Ctrl+C) | Serwer wysyła EXIT do klientów |
| Brak serwera przy starcie klienta | Klient kończy z błędem połączenia |

---

## Struktura plików

| Plik | Opis |
|------|------|
| `server.py` | Serwer gry - zarządzanie stanem, walidacja, broadcast |
| `client.py` | Klient z GUI pygame |
| `board.py` | Logika planszy - walidacja ruchów, sprawdzanie wygranej |

---

## Reprezentacja planszy

Plansza to tablica 8x8 gdzie:
- `0` - puste pole
- `1` - owca
- `2` - wilk

Indeksowanie: `board[wiersz][kolumna]`, wiersz 0 = góra planszy.
