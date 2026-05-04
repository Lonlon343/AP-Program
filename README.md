# Notes API

Notizverwaltungs-REST-API, entwickelt im Rahmen des Kurses **Angewandte Programmierung** (2. Semester).

---

## Technologien

| Tool | Verwendung |
|------|------------|
| **FastAPI** | Web-Framework |
| **SQLModel** | ORM (SQLAlchemy + Pydantic) |
| **SQLite** | Datenbank (`notes.db`) |
| **uv** | Paketverwaltung |
| **pytest** + **requests** | Tests |

---

## Starten

```bash
uv run fastapi dev
```

- API: `http://127.0.0.1:8000`
- Interaktive Dokumentation: `http://127.0.0.1:8000/docs`

---

## Datenmodell

Notizen und Tags sind über eine **Many-to-Many**-Beziehung verknüpft:

```
NoteDB  ←→  NoteTagLink  ←→  Tag
```

- Tags werden automatisch kleingeschrieben und dedupliziert

---

## API-Endpunkte

### Notizen

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `POST` | `/notes` | Neue Notiz erstellen |
| `GET` | `/notes` | Alle Notizen abrufen (mit Filtern) |
| `GET` | `/notes/{note_id}` | Einzelne Notiz abrufen |
| `PUT` | `/notes/{note_id}` | Vollständiges Update (alle Felder) |
| `PATCH` | `/notes/{note_id}` | Teilweises Update (nur geänderte Felder) |
| `DELETE` | `/notes/{note_id}` | Notiz löschen |
| `GET` | `/notes/stats` | Statistiken (Anzahl, Kategorien, Top-Tags) |

**Filterparameter für `GET /notes`:**
```
?category=Arbeit    → nach Kategorie filtern
?search=python      → in Titel und Inhalt suchen
?tag=wichtig        → nach Tag filtern
```

### Tags

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `GET` | `/tags` | Alle Tags abrufen (sortiert) |
| `GET` | `/tags/{tag_name}/notes` | Alle Notizen mit einem bestimmten Tag |

### Kategorien

| Methode | Endpunkt | Beschreibung |
|---------|----------|--------------|
| `GET` | `/categories` | Alle Kategorien abrufen (sortiert) |
| `GET` | `/categories/{category_name}/notes` | Alle Notizen einer Kategorie |

---

## Tests ausführen

Zuerst den Server starten, dann in einem zweiten Terminal:

```bash
uv run pytest test_notes.py -v
```

### Testabdeckung (29 Tests)

| Bereich | Beschreibung |
|---------|--------------|
| CRUD (5) | Erstellen, Auflisten, Abrufen, Aktualisieren, Löschen |
| Filterung (4) | Kategorie, Tag, Suche, kombinierte Filter |
| Fehlerfälle (4) | Fehlende Felder, nicht vorhandene IDs |
| Statistiken & PATCH (5) | Stats-Endpunkt, teilweise Updates, Kategorien |
| Tag-Endpunkte (2) | `/tags`, `/tags/{name}/notes` |
| Sonderfälle (4) | Leerer Titel, langer Inhalt, Sonderzeichen, Unicode |
| Datenbank (3) | Beziehungen, Many-to-Many, Persistenz |
| Parametrisiert (3) | Kategorien Work / Personal / Study |

---

## Projektstruktur

```
.
├── main.py              # FastAPI-App mit allen Endpunkten
├── test_notes.py        # Testsuite (pytest + requests)
├── notes.db             # SQLite-Datenbank (automatisch erstellt)
├── data/
│   └── notes.json       # Alte JSON-Speicherung (nicht mehr aktiv)
├── pyproject.toml       # Abhängigkeiten (uv)
└── README.md
```
