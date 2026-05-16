# Notes API

Notizverwaltungs-REST-API mit Streamlit-Frontend, entwickelt im Rahmen des Kurses **Angewandte Programmierung** (2. Semester).

---

## Technologien

| Tool | Verwendung |
|------|------------|
| **FastAPI** | Web-Framework (REST API) |
| **SQLModel** | ORM (SQLAlchemy + Pydantic) |
| **SQLite** | Datenbank (`notes.db`) |
| **Pydantic** | Eingabe-Validierung |
| **Streamlit** | Web-Frontend |
| **uv** | Paketverwaltung |
| **pytest** + **requests** | Tests |

---

## Starten

### Backend (FastAPI)

```bash
uv run fastapi dev main.py
```

- API: `http://127.0.0.1:8000`
- Interaktive Dokumentation: `http://127.0.0.1:8000/docs`

### Frontend (Streamlit)

```bash
uv run streamlit run frontend.py
```

> Backend muss laufen, bevor das Frontend gestartet wird.

---

## Datenmodell

Notizen und Tags sind über eine **Many-to-Many**-Beziehung verknüpft:

```
NoteDB  ←→  NoteTagLink  ←→  Tag
```

### Eingabe (`NoteCreate`)

| Feld | Typ | Regeln |
|------|-----|--------|
| `title` | `str` | 3–100 Zeichen, kein reiner Whitespace |
| `content` | `str` | 1–10.000 Zeichen |
| `category` | `str` | Muss einer der erlaubten Werte sein |
| `tags` | `list[str]` | Max. 10, je min. 2 Zeichen; werden lowercase + dedupliziert |
| `author_email` | `EmailStr \| None` | Optional, muss gültige E-Mail-Adresse sein |
| `priority` | `int` | 1–5, Standard: 3 |
| `created_at` | `datetime \| None` | Optional; darf nicht in der Zukunft liegen |

**Erlaubte Kategorien:** `work`, `personal`, `school`, `ideas`, `general`

### Ausgabe (`NoteResponse`)

```json
{
  "id": 1,
  "title": "Beispiel",
  "content": "Inhalt",
  "category": "work",
  "tags": ["urgent", "meeting"],
  "created_at": "2025-05-12T10:00:00"
}
```

---

## API-Endpunkte

### Notizen

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `POST` | `/notes` | Neue Notiz erstellen |
| `GET` | `/notes` | Alle Notizen abrufen (mit Filtern) |
| `GET` | `/notes/{note_id}` | Einzelne Notiz abrufen |
| `PUT` | `/notes/{note_id}` | Vollständiges Update (alle Felder erforderlich) |
| `PATCH` | `/notes/{note_id}` | Teilweises Update (nur gesendete Felder werden geändert) |
| `DELETE` | `/notes/{note_id}` | Notiz löschen (204 No Content) |
| `GET` | `/notes/stats` | Statistiken (Anzahl, Kategorien, Top-5-Tags) |

**Filterparameter für `GET /notes`:**

| Parameter | Beispiel | Beschreibung |
|-----------|----------|--------------|
| `category` | `?category=work` | Nach Kategorie filtern |
| `search` | `?search=meeting` | Volltextsuche in Titel und Inhalt (case-insensitiv) |
| `tag` | `?tag=urgent` | Nach Tag filtern |
| `created_after` | `?created_after=2025-01-01T00:00:00` | Nur Notizen nach diesem Zeitpunkt |
| `created_before` | `?created_before=2025-12-31T23:59:59` | Nur Notizen vor diesem Zeitpunkt |

Filter können kombiniert werden:
```
GET /notes?category=work&tag=urgent&search=meeting
```

### Tags

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `GET` | `/tags` | Alle Tags abrufen (sortiert, dedupliziert) |
| `GET` | `/tags/{tag_name}/notes` | Alle Notizen mit einem bestimmten Tag |

### Kategorien

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `GET` | `/categories` | Alle Kategorien abrufen (sortiert) |
| `GET` | `/categories/{category_name}/notes` | Alle Notizen einer Kategorie |

### Sonstiges

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `GET` | `/` | Root / Metadaten |
| `GET` | `/name/{name}` | Begrüßung per Pfadparameter |
| `GET` | `/age/{age}` | Altersüberprüfung |
| `GET` | `/add/{num1}/{num2}` | Addition zweier Zahlen |
| `GET` | `/queryparameters` | Demo für Query-Parameter |

---

## Tests ausführen

Backend muss laufen, dann im zweiten Terminal:

```bash
# Haupt-Testsuite (empfohlen)
uv run pytest test_suite.py -v

# Grundlegende CRUD-Tests
uv run pytest test_main.py -v

# Validierungstests
uv run pytest test_validation.py -v

# Alle Tests
uv run pytest -v

# Performance-Tests separat ausführen
uv run pytest test_suite.py -v -m performance

# Performance-Tests überspringen
uv run pytest test_suite.py -v -m "not performance"
```

### Testdateien

| Datei | Inhalt |
|-------|--------|
| `test_suite.py` | Vollständige Referenz-Suite: CRUD, Filter, Statistiken, PATCH/PUT-Semantik, Tag-Normalisierung, Validierung (422), Performance-Tests |
| `test_main.py` | Grundlegende CRUD-Tests, Filterung, Edge Cases, Datenbankbeziehungen, parametrisierte Kategorientests |
| `test_validation.py` | Pydantic-Validierung: Titellänge, Kategorien, Tag-Normalisierung, `extra=forbid`, Work-Tag-Regel |

---

## Aufbau eines API-Endpunkts

Am Beispiel `POST /notes`:

```python
@app.post("/notes", status_code=201)          # 1. Route + HTTP-Methode + Statuscode
def create_note(note: NoteCreate,             # 2. Request-Body wird automatisch validiert
                session: SessionDep           #    Datenbankverbindung per Dependency Injection
               ) -> NoteResponse:             # 3. Rückgabetyp (FastAPI serialisiert automatisch)

    db_note = NoteDB(                         # 4. Pydantic-Input → DB-Modell umwandeln
        title=note.title,
        content=note.content,
        category=note.category
    )

    session.add(db_note)                      # 5. In die Datenbank schreiben
    session.commit()
    session.refresh(db_note)                  #    Generierte ID + Beziehungen nachladen

    return NoteResponse(                      # 6. DB-Modell → Response-Modell zurückgeben
        id=db_note.id,
        title=db_note.title,
        ...
    )
```

**Ablauf einer Anfrage:**

```
HTTP POST /notes  →  Pydantic validiert Body  →  Endpoint-Funktion  →  SQLite  →  NoteResponse (JSON)
                          ↓ Fehler                                          ↑
                       422 Unprocessable Entity                    Dependency Injection
                                                                   liefert DB-Session
```

**Die drei Modelle im Überblick:**

| Modell | Zweck | Besonderheit |
|--------|-------|--------------|
| `NoteCreate` | Eingabe (Request Body) | Validierung, `extra="forbid"` |
| `NoteDB` | Datenbank | SQLModel-Tabelle mit Beziehungen |
| `NoteResponse` | Ausgabe (JSON) | Nur öffentliche Felder, kein Passwort/intern |

---

## Projektstruktur

```
.
├── main.py              # FastAPI-App (Endpunkte, Modelle, Datenbanklogik)
├── frontend.py          # Streamlit-Frontend (Erstellen, Anzeigen, Löschen)
├── test_suite.py        # Referenz-Testsuite (pytest + requests)
├── test_main.py         # Grundlegende API-Tests
├── test_validation.py   # Validierungstests
├── notes.db             # SQLite-Datenbank (automatisch erstellt)
├── pyproject.toml       # Abhängigkeiten (uv)
├── data/
│   └── notes.json       # Alte JSON-Speicherung (nicht mehr aktiv)
└── exploration/
    ├── class_based_decorator.py  # Klassen-basierte Dekoratoren (Call-Counter, Cache)
    ├── api_tests.py              # Frühe API-Experimente
    ├── main_day4.py              # Tag-4-Experimente
    └── test-day-4.py            # Tag-4-Tests
```

Wenn Tests nicht durchlaufen, fastapi server neu starten!