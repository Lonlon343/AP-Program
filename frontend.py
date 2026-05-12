"""
# Streamlit installieren
# Streamlit app hello world erstellen
# Say no app als ersten Test erstellen
 - API: https://docs.streamlit.io/library/api-reference
 - API endpoint: 
 - Button in Streamlit, der bei Klick an Endpoint sendet und Antwort anzeigt

 Todo's:
 - 2 Funktionen von Notizen mit Streamlit App verbinden
 - Funktion 1: Alle Notizen anzeigen (Liste von Notizen mit Titel, Inhalt dynamisch anzeigen)
   - Liste von Titeln von Notizen anzeigen
   - Moeglichkeit zu einem Titel den Inhalt, Tags, Category anzuzeigen 
 - Funktion 2: Neue Notiz erstellen (Formular mit Titel, Inhalt, Button)
   - Erstellen einer neuen Notiz
   - Neu erstellte Notiz soll in Liste auftauchen
"""

import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"



# --- API Funktionen ---
def get_notes():
    try:
        resp = requests.get(f"{API_URL}/notes")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Fehler beim Laden der Notizen: {e}")
        return []

def create_note(title, content, category, tags):
    payload = {
        "title": title,
        "content": content,
        "category": category,
        "tags": tags,
    }
    try:
        resp = requests.post(f"{API_URL}/notes", json=payload)
        resp.raise_for_status()
        return True, resp.json()
    except Exception as e:
        st.error(f"Fehler beim Erstellen: {e}")
        return False, None

st.title("Notiz-App (Streamlit + FastAPI)")

# --- Session State initialisieren ---
if "note_created" not in st.session_state:
    st.session_state.note_created = False
if "delete_result" not in st.session_state:
    st.session_state.delete_result = None  # None | "success" | "error"

# --- Neue Notiz erstellen ---
st.header("Neue Notiz anlegen")
with st.form("create_note_form"):
    title = st.text_input("Titel")
    content = st.text_area("Inhalt")
    category = st.selectbox("Kategorie", ["general", "work", "personal", "school", "ideas"])
    tags = st.text_input("Tags (Komma-getrennt)")
    submitted = st.form_submit_button("Erstellen")
    if submitted:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        ok, result = create_note(title, content, category, tag_list)
        st.session_state.note_created = ok

# Rückmeldung außerhalb des Forms — kein st.rerun(), damit die Meldung sichtbar bleibt
if st.session_state.note_created:
    st.balloons()
    st.success("✅ Notiz erfolgreich erstellt!")
    st.session_state.note_created = False


# --- Notiz per ID löschen ---
def delete_note(note_id: int) -> bool:
    try:
        resp = requests.delete(f"{API_URL}/notes/{note_id}")
        resp.raise_for_status()
        return True
    except Exception:
        return False

st.header("Notiz löschen")
all_notes = get_notes()
if not all_notes:
    st.info("Keine Notizen vorhanden.")
else:
    note_options = {f"[ID {n['id']}] {n['title']}": n["id"] for n in all_notes}
    with st.form("delete_note_form"):
        selected = st.selectbox("Notiz auswählen", options=list(note_options.keys()))
        delete_submitted = st.form_submit_button("Löschen")
        if delete_submitted:
            st.session_state.delete_result = "success" if delete_note(note_options[selected]) else "error"
            st.session_state.delete_id = note_options[selected]
            st.session_state.delete_title = selected

if st.session_state.delete_result == "success":
    st.success(f"✅ {st.session_state.delete_title} wurde gelöscht!")
    st.session_state.delete_result = None
    st.rerun()
elif st.session_state.delete_result == "error":
    st.error(f"Fehler beim Löschen.")
    st.session_state.delete_result = None


# --- Alle Notizen anzeigen (max. 20) ---
st.header("Alle Notizen (max. 20)")
notes = get_notes()
if not notes:
    st.info("Keine Notizen gefunden.")
else:
    for note in notes[:20]:
        with st.expander(note["title"]):
            st.write(f"**Inhalt:** {note['content']}")
            st.write(f"**Kategorie:** {note['category']}")
            st.write(f"**Tags:** {', '.join(note['tags']) if note['tags'] else '-'}")
            st.write(f"**Erstellt am:** {note['created_at']}")

st.map(
    data={"lat": [50.241218], "lon": [11.321113], "name": ["Coburg"]},
    zoom=2,
    use_container_width=True,
)   

date = st.date_input("Pick a date. los!")
