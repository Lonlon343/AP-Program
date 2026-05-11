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

def delete_note(note_id):
    try:
        resp = requests.delete(f"{API_URL}/notes/{note_id}")
        resp.raise_for_status()
        return True
    except Exception as e:
        return False

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
    except requests.exceptions.ConnectionError:
        return False, "API nicht erreichbar – läuft der FastAPI Server? (uvicorn main:app)"
    except Exception as e:
        detail = ""
        if hasattr(e, "response") and e.response is not None:
            try:
                detail = e.response.json().get("detail", "")
            except Exception:
                detail = e.response.text
        return False, detail or str(e)



st.title("Notiz-App (Streamlit + FastAPI)")

# --- Neue Notiz erstellen ---
st.header("Neue Notiz anlegen")

if "note_created" not in st.session_state:
    st.session_state.note_created = False
if "note_error" not in st.session_state:
    st.session_state.note_error = ""

with st.form("create_note_form"):
    title = st.text_input("Titel")
    content = st.text_area("Inhalt")
    category = st.selectbox("Kategorie", ["general", "work", "personal", "school", "ideas"])
    tags = st.text_input("Tags (Komma-getrennt)")
    submitted = st.form_submit_button("Erstellen")
    if submitted:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        ok, result = create_note(title, content, category, tag_list)
        if ok:
            st.session_state.note_created = True
            st.session_state.note_error = ""
        else:
            st.session_state.note_error = result
            st.session_state.note_created = False

if st.session_state.note_error:
    st.error(f"Fehler: {st.session_state.note_error}")

if st.session_state.note_created:
    st.toast("Notiz erfolgreich erstellt!", icon="✅")
    st.session_state.note_created = False
    st.rerun()

# --- Notiz per ID löschen ---
st.header("Notiz per ID löschen")

if "delete_error" not in st.session_state:
    st.session_state.delete_error = ""

with st.form("delete_note_form"):
    note_id = st.number_input("Notiz-ID", min_value=1, step=1)
    submitted_delete = st.form_submit_button("Löschen")
    if submitted_delete:
        if delete_note(int(note_id)):
            st.session_state.delete_error = ""
            st.toast(f"Notiz mit ID {int(note_id)} gelöscht!", icon="🗑️")
            st.rerun()
        else:
            st.session_state.delete_error = f"Notiz mit ID {int(note_id)} nicht gefunden."

if st.session_state.delete_error:
    st.error(st.session_state.delete_error)

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
            if st.button("🗑️ Löschen", key=f"delete_{note['id']}"):
                if delete_note(note["id"]):
                    st.toast(f"Notiz '{note['title']}' gelöscht!", icon="🗑️")
                    st.rerun()
                else:
                    st.error("Fehler beim Löschen.")

