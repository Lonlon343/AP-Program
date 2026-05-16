# Work Log

**Student Name: Leon Hartling** 

Instructions: Fill out one log for each course day. Content to consider: Course Sessions + Assignment

## Week 1

### Day 1

#### 1. ✅ What did I accomplish?

Am ersten Tag haben wir zuerst ein paar Python-Grundlagen aufgefrischt und sind dann direkt in die Welt der Web-APIs eingestiegen. Konkret habe ich mit FastAPI meine erste eigene API-Anwendung aufgesetzt und mehrere einfache Endpoints gebaut. Dabei habe ich gelernt, wie ein FastAPI-Projekt grundsätzlich aufgebaut ist und wie die automatisch generierte interaktive Doku unter /docs (Swagger UI) funktioniert. Das war für mich spannend, weil ich bisher zwar mehrere APIs benutzt habe — aber immer nur als Konsument mit API-Schlüssel. Selbst eine zu bauen hat mir ein deutlich besseres Verständnis dafür gegeben, was eigentlich auf der "anderen Seite" einer HTTP-Anfrage passiert.

---

#### 2. 🚧 What challenges did I face?

Inhaltlich lief der erste Tag weitgehend reibungslos — die Grundkonzepte (Routes, Rückgabe von Dictionaries als JSON) waren gut nachvollziehbar. Eine offene Frage ist mir aber geblieben: Wie integriere ich einen API-Call sinnvoll in eine Webseite, ohne die URL manuell im Browser aufzurufen? Mir war zu dem Zeitpunkt noch nicht klar, wie der Übergang von "ich tippe /add/2/3 in die Adresszeile" zu einem echten Frontend funktioniert, das im Hintergrund mit der API kommuniziert.

---

#### 3. 💡 How did I overcome them?

Da es am ersten Tag keine größeren Hürden gab, ging es vor allem darum, mir die offene Frage für später zu merken. Ich habe sie als offenen Punkt im Hinterkopf behalten. Außerdem habe ich mir die Swagger-UI unter /docs als praktisches Werkzeug gemerkt, um Endpoints zu testen.

---

### Day 2

#### 1. ✅ What did I accomplish?

Wir haben mehrere API Calls erstellt mit unterschiedlichen Aufgaben. Wir haben eine kleine Notiz-Verwaltung umgesetzt, bei der Notizen in einer JSON-Datei (data/notes.json) gespeichert werden. Der API Aufruf erstellt Notizen mit eigen benannten Strings in einer JSON-Datei mit POST. Mit GET kann man ueber Fastapi, die Dateien aufrufen und einordnen. Dadurch werden sie dann z.B. nach Kategorie oder Anzahl aufgelistet. Außerdem haben wir zwei zentrale Hilfsfunktionen geschrieben: load_notes() liest die JSON-Datei beim Start eines Endpoints ein, parst die Einträge in Note-Objekte und gibt zusätzlich den nächsten freien ID-Counter zurück. save_notes(notes_db) schreibt die aktuelle Liste nach jeder Änderung zurück in die Datei. Damit hatte ich zum ersten Mal CRUD Vorgang in FastAPI implementiert.

---

#### 2. 🚧 What challenges did I face?

Schema-Konflikt nach dem Hinzufügen von category: 
Als ich das Feld category neu aufgenommen habe, konnte ich keine neue Notiz mehr erstellen. Beim Start ist load_notes() fehlgeschlagen, weil in der bestehenden notes.json noch Einträge ohne category lagen — Pydantic hat das beim Parsen als Validierungsfehler abgelehnt und damit die ganze Datei unbenutzbar gemacht.

Verwirrung um den Rückgabetyp von load_notes(): 
Die Funktion gibt ein Tupel zurück (notes_db, note_id_counter), nicht nur die Liste. Mir war zuerst nicht klar, warum ich notes_db, _ = load_notes() schreiben muss und was der Unterstrich bedeutet.

Wiederholtes Laden in jedem Endpoint: 
Beim Statistik-Endpoint musste ich notes_db erneut über load_notes() holen, obwohl ich gefühlt schon "alles geladen" hatte. Das hat sich zuerst unnötig redundant angefühlt.


---

#### 3. 💡 How did I overcome them?

Den Schema-Konflikt habe ich gelöst, indem ich die alte notes.json geleert habe. Damit war klar: Sobald sich das Datenmodell ändert, muss entweder die Datei mit migriert werden, oder die alten Daten passen einfach nicht mehr.

Das Tupel-Unpacking habe ich verstanden, nachdem ich mir die load_notes()-Funktion nochmal genau angeschaut habe: Sie liefert sowohl die Liste der Notizen als auch den nächsten freien ID-Zähler zurück.

Beim wiederholten Laden habe ich verstanden, warum das so sein muss: Da der API-Server zustandslos zwischen den Requests ist und die Daten in einer Datei liegen, muss jeder Endpoint, der auf den aktuellen Datenbestand zugreifen will, ihn frisch einlesen — sonst arbeitet man mit veralteten Daten.

---

### Day 3

#### 1. ✅ What did I accomplish?

Der Tag hatte zwei Schwerpunkte: die theoretischen Grundlagen von REST-API-Design und in der Praxis das Erweitern der Notiz-API zu einem vollständigen CRUD-Service, gefolgt von der Migration von JSON-Daten auf eine SQL-Datenbank über SQLModel.
REST-Konzepte: Wir haben uns angeschaut, was REST eigentlich bedeutet — ressourcenorientiertes Design, also Substantive in URLs (/notes statt /getNotes) und HTTP-Methoden mit klar definierter Semantik (GET = lesen, POST = anlegen, PUT = ersetzen, PATCH = teilweise ändern, DELETE = löschen). Dazu kam der Unterschied zwischen Path-Parametern zur Identifikation einer Ressource (/notes/{id}) und Query-Parametern zum Filtern einer Sammlung (/notes?category=work), sowie die passenden HTTP-Statuscodes (200, 201, 204, 404, 422).
API-Erweiterungen: Aufbauend auf der Tag-2-Version habe ich gebaut:

- einen Query-Parameter-Endpoint GET /queryparameters zum Filtern einer Namensliste nach Substring

- Filter im GET /notes-Endpoint für category, search, tag, created_before und created_after

- den PUT /notes/{note_id}-Endpoint für vollständige Updates und PATCH /notes/{note_id} für Teil-Updates über ein eigenes NoteUpdate-Modell mit optionalen Feldern,

- den DELETE /notes/{note_id}-Endpoint mit Statuscode 204 (No Content),

- den Statistik-Endpoint GET /notes/stats mit total_notes, by_category, top_tags (Top 5) und unique_tags_count

- Resource-Relationship-Endpoints nach dem Muster /tags/{tag_name}/notes und /categories/{category_name}/notes

- HTTPException für nicht existierende Notizen und ungültige Eingaben.

Datenbank-Migration (Task 6): Den zweiten Block haben wir mit SQLModel umgesetzt:

- SQLite über engine = create_engine("sqlite:///notes.db") angebunden

- zwei Tabellen-Modelle definiert: NoteDB und Tag,

- eine Many-to-Many-Beziehung zwischen Notizen und Tags über die Linktabelle NoteTagLink umgesetzt

- alle bestehenden Endpoints von der JSON-Datei auf die Datenbank umgestellt, inklusive Session-Handling über Depends(get_session) und einem SessionDep-Type-Alias,

- die Trennung zwischen API-Modellen (NoteCreate, NoteResponse) und Datenbankmodell (NoteDB) eingeführt.

Bei GET/notes/stats ist mir aufgefallen, dass ich beim return command keine Tags angeben muss und trotzdem alle Informationen zu allen Notes bekomme. Außerdem habe ich gelernt, warum man Zahlen wie Telefonnummern als String und nicht als Integer speichert (führende Nullen, Plus-Zeichen, Formatierung).

---

#### 2. 🚧 What challenges did I face?

Statistik-Endpoint: Beim Bauen der top_tags-Liste war mir zuerst nicht klar, dass ein Counter sinnvoll wäre. Mein erster Output enthielt zwar die richtigen Tags, aber ohne Häufigkeit:

{
  "total_notes": 7,
  "by_category": {
    "study": 3,
    "test": 1,
    "work": 1,
    "life": 1,
    "business": 1
  },
  "top_tags": [
    "work",
    "urgent",
    "meeting"
  ],
  "unique_tags_count": 4
}

Ich habe nicht gesehen, dass wir counter implementieren sollten, deswegen habe ich geschaut, wie ich das ohne counter erstellen kann und es scheint zu funktionieren.

Task 6:
Sqlmodel ließ sich nicht importieren, weil es im falschen Environment installiert war. Ich hatte pip und uv parallel benutzt und dabei zwei verschiedene Umgebungen erzeugt.

Datenbankmodell-Aufbau: Bei der ersten Version waren die SQLModel-Klassen falsch verschachtelt — Tag lag innerhalb von Note, die Einrückungen stimmten nicht. Außerdem fehlte die Linktabelle NoteTagLink für die Many-to-Many-Beziehung. Dazu kam ein Namenskonflikt zwischen dem Pydantic-Modell aus der API-Schicht und dem SQLModel der Datenbank, weil beide Note hießen, daher umbenennung der SQL table class.

Reihenfolge der Codeblöcke: Mehrfach Fehler, weil Klassen oder Funktionen referenziert wurden, bevor sie definiert waren — der Editor hat die Instanz als „unbekannt" markiert.

Nicht immer einfach herauszufinden, warum die geupdateten API endpoints nicht auf die notes.db SQL Database gerichtet sind.

Endpoint-Migration auf SQL: Manche Endpoints schienen weiterhin auf die alten JSON-Daten zuzugreifen statt auf notes.db. Außerdem brauchen Tags in SQLModel Tag-Objekte, keine Strings — das war ohne Vorwissen zu SQL-Beziehungen aus den Fehlermeldungen heraus nicht direkt erkennbar.

Benennung in Fehlerprüfungen: Bei den if not ...-Abfragen war mir nicht immer klar, ob die Variable note oder notes heißt und worauf sich die Prüfung jeweils bezieht.


---

#### 3. 💡 How did I overcome them?

Statistik: Nach Recherche und Rückfrage an die KI habe ich den Counter weggelassen und stattdessen mit einem Dictionary (tag_counts[tag] = tag_counts.get(tag, 0) + 1) gezählt, sortiert, und auf die Top 5 reduziert.

Environment-Problem: Copilot hat nach dem Hinweis „Projekt läuft mit uv" das Problem schnell eingegrenzt und sqlmodel über das Terminal in die richtige Umgebung installiert.

Datenbankmodell: Mit Hilfe der KI habe ich das Modell umstrukturiert: Tag als eigene Klasse auf gleicher Ebene wie NoteDB, NoteTagLink als explizite Linktabelle, und die Pydantic-API-Klasse zur Unterscheidung umbenannt — daher NoteDB für die Tabelle und NoteCreate / NoteResponse für die API-Schicht.

Tag-Objekte statt Strings: Im POST-Endpoint baue ich für jeden Tag-String aus dem Request entweder ein bestehendes Tag-Objekt aus der Datenbank (über select(Tag).where(Tag.name == ...)) oder lege ein neues an. Erst diese Liste von Objekten weise ich db_note.tags zu.

Benennung note vs. notes: Die Regel hängt vom Rückgabetyp der DB-Abfrage ab:

- session.get(NoteDB, note_id) → einzelnes Objekt oder None → Variable note → if not note prüft auf None
- session.exec(...).all() → immer eine Liste, ggf. [] → Variable notes → if not notes prüft auf leere Liste

Reihenfolge der Codeblöcke: Ich habe mir angewöhnt, Datenbankmodelle ganz oben zu definieren, danach Hilfsfunktionen und erst dann die Endpoints, damit Referenzen in der richtigen Reihenfolge stehen.

---

## Week 2

### Day 4

#### 1. ✅ What did I accomplish?

In der ersten Hälfte haben wir uns mit POST-Endpoints und Pydantic-Validierung beschäftigt, Statuscodes (201 Created bei Erfolg, 409 Conflict bei Duplikaten, 422 Unprocessable Entity bei Validierungsfehlern) sowie die automatische Validierung über Typannotationen.

In der zweiten Hälfte ging es um das Schreiben einer Testsuite mit pytest für die bestehende Notiz-API. Wir haben die beiden gängigen Ansätze gegenübergestellt — externes Testen mit requests gegen einen laufenden Server versus internes Testen mit TestClient ohne Serverprozess. Im Projekt haben wir eine Testdatei test_main.py aufgebaut.

Die Suite deckt die komplette API ab: für wiederverwendbare Testdaten gibt es Fixtures (note, note_id, seeded_notes) und eine Hilfsfunktion _create_note, damit der Test-Code übersichtlich bleibt. Inhaltlich getestet wird das gesamte CRUD-Verhalten (Erstellen mit 201, Lesen, Updaten mit PUT und PATCH, Löschen mit 204), 
alle Filter einzeln und in Kombination (category, search, tag, created_after, created_before), 
die Struktur und Sortierung des Statistik-Endpoints, 
die Tag-Normalisierung (Whitespace, Case-Insensitivität, Deduplizierung, Längenlimits), 
die PATCH-Semantik (leerer Body ändert nichts, Tags werden ersetzt statt angehängt) und eine Reihe von Validierungs- und Edge-Cases. Beim Schreiben der Tests habe ich mehrere Bugs in den Endpoints selbst gefunden und gefixt — vor allem inkonsistente Rückgaben (z. B. 404 statt leerer Liste bei unbekannten Tags), die ich erst durch das Testen bemerkt habe.

---

#### 2. 🚧 What challenges did I face?

Zunächst hatte ich Probleme mit Indentation-Fehlern beim Übernehmen der Test-Snippets aus der Präsentation. Da pytest-Tests  verschachtelte Aufrufe enthalten (zuerst ein Setup-POST, dann ein GET, dann Assertions), war mir nicht immer klar, auf welcher Einrückungsebene welcher Codeblock liegen muss. Die Fehlermeldung zeigt nicht immer auf die eigentliche Ursache.

Dazu kommt, dass alle Testdaten in derselben Datenbank landen wie die echten Daten. Jeder Testlauf erzeugt neue Notizen und Tags in notes.db, ohne dass am Ende wieder aufgeräumt wird. Mit der Zeit füllt sich die Datenbank mit Testresten und wird unübersichtlich. Ich habe nachgelesen, dass üblicherweise eine separate Testdatenbank verwendet wird.

---

#### 3. 💡 How did I overcome them?

Die Indentation-Fehler habe ich mit Hilfe der KI gelöst: Indem ich den fehlerhaften Block mit der Fehlermeldung zusammen zur Prüfung gegeben habe, ließen sich die Einrückungsebenen schnell richtigstellen. Im Laufe des Tages habe ich ein besseres Gefühl dafür entwickelt, wann eine neue Einrückungsebene gerechtfertigt ist (innerhalb einer Funktion, innerhalb eines for- oder if-Blocks) und wann nicht.

Für die Tests habe ich dann teilweise eine neue separate Datenbank erstellt, die ich daraufhin dann wieder entfernt habe, damit sich nicht tausende Notizen ansammeln (sqlite:///test_notes.db).

---

### Day 5

#### 1. ✅ What did I accomplish?

An Tag 5 haben wir Tests bei Teampartnern ausprobiert und auf deren jeweilige API-Endpunkte angepasst. Dabei fiel auf, dass Tests, die für eine API geschrieben wurden, sich nicht eins zu eins auf eine andere übertragen, auch wenn beide das gleiche Thema haben.

Pydantic Data Validation in die eigene API eingebaut: mit `Field()` wurden Längenbeschränkungen gesetzt, mit `@field_validator` eigene Regeln fuer Titel, Kategorie und Tags implementiert und mit `@model_validator` eine feldübergreifende Regel hinzugefügt.
Dadurch sind Eingaben jetzt klar eingeschränkt — ungültige Daten werden automatisch mit einem 422-Fehler abgelehnt, bevor sie in die Datenbank gelangen.

Zusätzlich wurde `NoteUpdate` fuer PATCH-Requests angepasst mit ähnlichen Einschränkungen und ein eigenes Test-File `test_validation.py` mit gezielten Validierungstests erstellt.


---

#### 2. 🚧 What challenges did I face?

Field und @field_validator waren neue Konzepte und ich musste erst reinkommen, damit zu arbeiten — vor allem, weil die Validatoren als @classmethod deklariert werden müssen und immer den (ggf. veränderten) Wert zurückgeben müssen. Vergisst man das return, läuft der Code ohne Fehlermeldung, aber die Normalisierung greift nicht.
Der Unterschied zwischen @field_validator und @model_validator war anfangs nicht klar. Dazu kam die Frage, wann ich mode="before" und wann mode="after" brauche — je nachdem, ob Pydantic den Wert vorher schon in den passenden Typ umgewandelt hat oder nicht.
Bei NoteUpdate für PATCH war ein zusätzlicher Stolperstein, dass die Validatoren None explizit durchlassen müssen. Sobald ein Feld nicht im Request mitgeschickt wird, kommt es als None in den Validator, und ohne eine entsprechende Abfrage am Anfang scheitert die Validierung an Operationen wie .strip().lower().


---

#### 3. 💡 How did I overcome them?


Fuer die Tests bei den Teampartnern habe ich deren Endpunkte vorher kurz in der /docs Seite angeschaut, um zu verstehen welche Felder benoetigt werden.

Um mich mit Field und field_validator vertraut zu machen, habe ich die Konzepte Schritt fuer Schritt ausprobiert. Zuerst einfache Längenbeschränkungen mit Field() eingebaut, dann schrittweise Validatoren hinzugefügt. Durch das direkte Testen ueber die /docs Oberflaeche von FastAPI konnte ich sehen, ob die Validierung wie erwartet funktioniert.

Beim Cross-Field Validator (model_validator) hat mir der Vergleich mit field_validator geholfen: Sobald ich verstanden hatte, dass field_validator immer nur ein Feld sieht, war klar warum model_validator noetig ist, wenn zwei Felder gleichzeitig geprueft werden muessen.

Für den None-Fall in NoteUpdate habe ich am Anfang jedes Validators eine Abfrage eingebaut (if v is None: return v), sodass das Feld nur dann normalisiert oder geprüft wird, wenn es tatsächlich im Request enthalten war.

---

### Day 6

#### 1. ✅ What did I accomplish?

Tag 6 hatte zwei Themen. Im ersten Teil ging es um Python-Decorators — also die @-Syntax (@app.get(...), @field_validator(...)). In der Übung haben wir einen eigenen Decorator gebaut, der wie ein einfacher Cache funktioniert: er umhüllt eine Funktion, merkt sich die Argumente und die zugehörigen Ergebnisse, und gibt beim wiederholten Aufruf mit denselben Argumenten direkt das gespeicherte Ergebnis zurück. Damit wurde nachvollziehbar, was hinter dem Decorator-Mechanismus steckt: eine Funktion bekommt eine andere Funktion übergeben, fügt ihr Verhalten hinzu und gibt sie wieder zurück. Zum Debuggen haben wir die Bibliothek icecream benutzt, die Funktionsaufrufe und Zwischenwerte mit ic(...) ausgibt.

Im zweiten Teil ging es um eine bereitgestellte Test-Suite vom Dozenten (test_main.py), die wir in unser eigenes Projekt einbinden und gegen unsere API zum Laufen bringen sollten. Beim ersten Durchlauf sind die meisten Tests durchgefallen, weil meine API an einigen Stellen anders reagiert hat als von den Tests erwartet — andere Statuscodes, andere Response-Bodies, oder Bedingungen, die zu strikt waren.

---

#### 2. 🚧 What challenges did I face?

Die größte Hürde war zu erkennen, warum ein Test fehlschlägt. Der Pytest-Output war nicht immer eindeutig: manchmal stand dort nur, dass Statuscode X erwartet wurde, aber Y kam — ohne dass klar war, ob das Problem im Endpoint, im Datenmodell, in der Validierung oder in den Testdaten lag. Mehrere Tests hingen voneinander ab oder bauten auf einem bestimmten Datenbankzustand auf, was die Fehlersuche zusätzlich erschwert hat.

Zwei konkrete Beispiele:
Die Test-Suite hat erwartet, dass Notiz mit der ID 1000 nicht existiert — und entsprechend 404 zurückkommt. In meiner Datenbank hatte sich aber durch viele vorherige Testläufe längst eine Notiz mit dieser ID angesammelt, weshalb der Endpoint stattdessen 200 zurückgegeben hat.

Beim DELETE-Endpoint musste ich herausfinden, dass ich Response aus FastAPI importieren und explizit zurückgeben muss, damit 204 No Content ohne Body zurückkommt — vorher hatte ich ein Dict zurückgegeben, was bei Statuscode 204 nicht erlaubt ist.

---

#### 3. 💡 How did I overcome them?

Ich habe in der Fast API Dokumentation nach einer Loesung gegen das Fehlschlagen der Tests gesucht. Zusaetzlich habe ich mir eine Analyse des Fehlerberichts von KI geben lassen und mir erklaeren lassen, was bei welcher API korrigiert werden muss. Ich habe explizit angegeben, dass sie mir keinen Code schreiben soll, sondern mir erklären soll, wie ich das Problem am besten lösen kann.
Einerseits haben Response-Formate und Statuscodes nicht zu den Test-Erwartungen gepasst — wie beim DELETE-Endpoint (Response(status_code=204) statt Dict) oder bei Endpoints, die 404 zurückgaben, wo die Test-Suite eine leere Liste [] erwartet hat (z. B. /tags/{name}/notes und /categories/{name}/notes, wenn der Tag oder die Kategorie noch nicht existiert). Diese Stellen habe ich gezielt umgebaut und im Code kommentiert, warum die Änderung nötig war.
Andererseits waren Validierungs- und Geschäftsregeln zu strikt für die Tests — zum Beispiel der model_validator, der work-Notizen ohne work-Tag abgelehnt hat. Den habe ich auskommentiert, weil er sonst alle Tests blockiert hätte, die work-Notizen ohne diesen Tag erstellen.
Das Problem mit der Notiz-ID 1000 habe ich gelöst, indem ich die Datenbankdatei gelöscht und die Tests gegen eine frische Datenbank laufen lassen habe. Damit hat sich nebenbei auch das Problem aus Tag 4 erledigt, dass die Datenbank durch viele Testläufe immer voller wurde. Die saubere Lösung wäre weiterhin eine separate Testdatenbank.

---

## Week 3

### Day 7

#### 1. ✅ What did I accomplish?

Einstieg in Streamlit — eine Python-Bibliothek für Frontend. Den Einstieg haben wir mit einer „Hello World"-App und einer „Say-no"-App gemacht: ein Streamlit-Button, der bei jedem Klick die öffentliche API https://naas.isalman.dev/no aufruft und eine zufällige Begründung anzeigt, mit der man „nein" sagen kann.

Ich habe damit angefangen, ein eigenes Streamlit-Frontend für die Notiz-API aufzubauen (frontend.py). Das Frontend kommuniziert über requests mit dem FastAPI-Backend auf http://127.0.0.1:8000 und stellt zwei Hauptfunktionen bereit:
Zum einen ein Formular zum Anlegen neuer Notizen über st.form, das Titel (st.text_input), Inhalt (st.text_area), eine Kategorie (st.selectbox mit den erlaubten Werten) und Tags (Komma-getrennt im Textfeld) entgegennimmt. Beim Absenden wird der Payload an POST /notes geschickt. Mit st.session_state und einer kleinen Statusvariable habe ich danach eine Erfolgsmeldung (st.success("✅ Notiz erfolgreich erstellt!")) inklusive st.balloons() eingebaut, damit klar erkennbar ist, dass die Notiz tatsächlich angelegt wurde.
Zum anderen eine Anzeige der vorhandenen Notizen: über st.expander lässt sich jede Notiz aufklappen, um Inhalt, Kategorie, Tags und Erstellungsdatum zu sehen. Weil sich durch die vielen Pytest-Läufe inzwischen hunderte Testnotizen in der Datenbank angesammelt hatten, habe ich die Anzeige auf die ersten 20 Einträge begrenzt.
Ergänzend habe ich noch eine Lösch-Funktion ergänzt: ein eigenes Formular mit einer selectbox, in der jede Notiz mit ID und Titel zur Auswahl steht, sowie einem Submit-Button, der ein DELETE /notes/{id} an die API schickt.

---

#### 2. 🚧 What challenges did I face?

Mein Hauptproblem trat direkt beim Erstellen der ersten Notiz auf: Ich hatte keine sichtbare Rückmeldung im UI, ob die Notiz tatsächlich angelegt wurde. Beim erneuten Laden der Liste tauchte sie auch nicht auf. Dadurch war zunächst nicht klar, ob das Formular gar nicht abschickt, ob der API-Call fehlschlägt, oder ob die Notiz an einer anderen Stelle landet.
Bei der Fehlersuche bin ich darauf gestoßen, dass ich im Verlauf der Test-Suite-Experimente in Tag 6 versehentlich eine zweite Datenbankdatei angelegt hatte. FastAPI hat die Notizen aus dem Frontend dort hineingeschrieben, während meine Liste aus einer anderen .db-Datei las — sie lagen also nur in der falschen Datenbank.

---

#### 3. 💡 How did I overcome them?

Die fehlende Rückmeldung habe ich gelöst, indem ich den Erfolgsstatus über st.session_state.note_created zwischengespeichert und außerhalb des Formulars ausgewertet habe. Das war notwendig, weil Streamlit das Skript bei jedem Submit von oben neu durchläuft — eine Erfolgsmeldung direkt im if submitted:-Block wäre nach dem Rerun sofort wieder weg gewesen. Mit dem Session-State-Pattern bleibt die Meldung sichtbar, bis sie einmal angezeigt wurde, und wird dann zurückgesetzt.
Das Problem mit der doppelten Datenbank habe ich gelöst, indem ich beide .db-Dateien gelöscht und in der main.py nur noch genau einen Pfad (sqlite:///notes.db) konfiguriert habe. Damit landen alle Notizen — egal ob aus dem Frontend, aus /docs oder aus der Test-Suite — wieder in derselben Datenbank, und die im Frontend erstellten Notizen erscheinen auch in der Liste.

---

### Day 8

#### 1. ✅ What did I accomplish?

Ziel war es heute, das Repository so vorzubereiten, dass der Prüfer es ohne Rückfragen durchgehen kann: also klare Dateinamen, eine konsistente Projektstruktur und ein reibungsloser Ablauf für die drei zentralen Befehle:

den FastAPI-Server starten (uv run fastapi dev main.py),
die bereitgestellte Test-Suite ausführen (uv run pytest test_main.py),
das Streamlit-Frontend starten (uv run streamlit run notes_streamlit.py).

Konkret habe ich die Dateien in die im Kurs vorgegebenen Namen umbenannt, damit die Befehle ohne Anpassungen funktionieren. Anschließend habe ich den kompletten Ablauf nochmal von Anfang an durchgespielt — Server hochgefahren, alle Tests laufen lassen, parallel das Frontend gestartet und eine Notiz angelegt, gelesen, aktualisiert und gelöscht — um sicherzustellen, dass nichts vom Umbenennen oder vom Aufräumen abhängt.

---

#### 2. 🚧 What challenges did I face?

Die Challenge war, dafür zu sorgen, dass nach dem Umbenennen und Aufräumen alles noch funktioniert. Die einzelnen Komponenten (Backend, Tests, Frontend) sind über Datei- und Datenbankpfade miteinander verbunden, und beim Verschieben oder Umbenennen reicht eine falsche Referenz, damit ein Teil nicht mehr läuft.

---

#### 3. 💡 How did I overcome them?

Ich bin den Ablauf, den der Prüfer voraussichtlich durchgeht, Schritt für Schritt selbst durchgegangen. Kritische Stellen habe ich entweder durch konsistente Benennung, einen klaren README-Eintrag oder einen aufräumenden Kommentar im Code entschärft.

---



# 🎉 Congratulations! You did it! 🎓✨












