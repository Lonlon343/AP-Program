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

import math
from collections import defaultdict

import plotly.graph_objects as go
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


# --- Alle Notizen anzeigen (max. 20 neueste) ---
st.header("Alle Notizen (max. 20 neueste)")
notes = get_notes()
if not notes:
    st.info("Keine Notizen gefunden.")
else:
    # Sortiere nach created_at, neueste zuerst
    sorted_notes = sorted(notes, key=lambda n: n["created_at"], reverse=True)
    for note in sorted_notes[:20]:
        with st.expander(note["title"]):
            st.write(f"**Inhalt:** {note['content']}")
            st.write(f"**Kategorie:** {note['category']}")
            st.write(f"**Tags:** {', '.join(note['tags']) if note['tags'] else '-'}")
            st.write(f"**Erstellt am:** {note['created_at']}")

# --- Tag-Netzwerk ---
st.header("Tag-Netzwerk")

def show_tag_network():
    notes = get_notes()
    if not notes:
        st.info("Keine Notizen vorhanden.")
        return

    # Häufigkeiten und Kookkurrenz aufbauen
    tag_counts = defaultdict(int)
    co_occurrence = defaultdict(int)

    for note in notes:
        tags = note.get("tags", [])
        for tag in tags:
            tag_counts[tag] += 1
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                pair = tuple(sorted([tags[i], tags[j]]))
                co_occurrence[pair] += 1

    if not tag_counts:
        st.info("Keine Tags vorhanden.")
        return

    tags_list = list(tag_counts.keys())
    n = len(tags_list)

    # Kreisförmiges Layout: Tags gleichmäßig auf einem Kreis verteilen
    positions = {}
    for i, tag in enumerate(tags_list):
        angle = 2 * math.pi * i / n
        positions[tag] = (math.cos(angle), math.sin(angle))

    # Kanten: zwei Tags sind verbunden, wenn sie auf derselben Notiz vorkommen
    edge_x, edge_y, edge_hover = [], [], []
    for (t1, t2), count in co_occurrence.items():
        x1, y1 = positions[t1]
        x2, y2 = positions[t2]
        edge_x += [x1, x2, None]
        edge_y += [y1, y2, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1.5, color="rgba(150,150,150,0.45)"),
        hoverinfo="none",
    )

    # Knoten: Größe = Anzahl Notizen, Farbe = Anzahl Notizen
    counts = [tag_counts[t] for t in tags_list]
    hover_labels = [
        f"<b>{t}</b><br>{tag_counts[t]} Notiz{'en' if tag_counts[t] != 1 else ''}"
        for t in tags_list
    ]

    node_trace = go.Scatter(
        x=[positions[t][0] for t in tags_list],
        y=[positions[t][1] for t in tags_list],
        mode="markers+text",
        text=tags_list,
        textposition="top center",
        hovertext=hover_labels,
        hoverinfo="text",
        marker=dict(
            size=[14 + 7 * c for c in counts],
            color=counts,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Notizen"),
            line=dict(width=1.5, color="white"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Verbindungen = Tags auf derselben Notiz",
            showlegend=False,
            hovermode="closest",
            margin=dict(t=50, b=20, l=20, r=20),
            height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    st.plotly_chart(fig, width='stretch')

    # Balkendiagramm: Tag-Häufigkeiten
    st.subheader("Tag-Häufigkeiten")
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    bar_fig = go.Figure(
        go.Bar(
            x=[t for t, _ in sorted_tags],
            y=[c for _, c in sorted_tags],
            marker_color=[c for _, c in sorted_tags],
            marker_colorscale="Viridis",
            hovertemplate="%{x}: %{y} Notiz(en)<extra></extra>",
        )
    )
    bar_fig.update_layout(
        xaxis_title="Tag",
        yaxis_title="Anzahl Notizen",
        margin=dict(t=20, b=40, l=40, r=20),
        height=300,
    )
    st.plotly_chart(bar_fig, use_container_width=True)

show_tag_network()


st.map(
    data={"lat": [50.241218], "lon": [11.321113], "name": ["Coburg"]},
    zoom=2,
    use_container_width=True,
)   

date = st.date_input("Datum auswählen ohne Grund")