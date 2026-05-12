import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"

# Hilfsfunktion: gültige Note als Ausgangsbasis
def valid_note(**overrides):  # ermöglicht Überschreiben von Feldern
    data = {
        "title": "Valid Title",
        "content": "Some content here",
        "category": "general",
        "tags": ["python", "test"],
    }
    data.update(overrides)
    return data


def test_create_note_rejects_short_title():  # pytest erkennt Funktionen, die mit test_ beginnen, automatisch als Tests
    """Titel mit weniger als 3 Zeichen → 422"""
    response = requests.post(f"{BASE_URL}/notes", json=valid_note(title="Hi"))
    assert response.status_code == 422


def test_create_note_rejects_unknown_category():  
    """Unbekannte Kategorie → 422"""
    response = requests.post(f"{BASE_URL}/notes", json=valid_note(category="banana"))
    assert response.status_code == 422


def test_create_note_normalizes_tags():  
    """Tags werden zu lowercase, Duplikate werden entfernt"""
    response = requests.post(
        f"{BASE_URL}/notes",
        json=valid_note(category="general", tags=["PYTHON", "python", "  Test  "]),
    )
    assert response.status_code == 201
    tags = response.json()["tags"]
    assert "python" in tags
    assert "test" in tags
    # Duplikat "python"/"PYTHON" darf nur einmal vorkommen
    assert tags.count("python") == 1


def test_create_note_forbids_extra_fields():
    """Unbekannte Felder im Body → 422 (extra='forbid')"""
    payload = valid_note()
    payload["unknown_field"] = "should not be allowed"
    response = requests.post(f"{BASE_URL}/notes", json=payload)
    assert response.status_code == 422


def test_work_note_requires_work_tag():
    """category='work' ohne 'work' in tags → 422"""
    response = requests.post(
        f"{BASE_URL}/notes",
        json=valid_note(category="work", tags=["urgent"]),
    )
    assert response.status_code == 422


def test_work_note_with_work_tag_succeeds(): # positiver Gegentest zum vorherigen Test
    """category='work' mit 'work' in tags → 201"""
    response = requests.post(
        f"{BASE_URL}/notes",
        json=valid_note(category="work", tags=["work", "urgent"]),
    )
    assert response.status_code == 201


def test_patch_with_empty_body_succeeds():
    """PATCH mit leerem Body darf die Note nicht verändern → 200"""
    # Erst eine Note erstellen
    create = requests.post(f"{BASE_URL}/notes", json=valid_note())
    assert create.status_code == 201
    note_id = create.json()["id"]

    response = requests.patch(f"{BASE_URL}/notes/{note_id}", json={})
    assert response.status_code == 200


def test_patch_with_invalid_title_fails():
    """PATCH mit leerem Titel → 422"""
    create = requests.post(f"{BASE_URL}/notes", json=valid_note())
    assert create.status_code == 201
    note_id = create.json()["id"]

    response = requests.patch(f"{BASE_URL}/notes/{note_id}", json={"title": ""})
    assert response.status_code == 422


def test_tag_name_rejects_uppercase():
    """Tag mit Großbuchstaben wird normalisiert — kein 422 erwartet,
    aber der gespeicherte Tag muss lowercase sein"""
    response = requests.post(
        f"{BASE_URL}/notes",
        json=valid_note(tags=["UPPERCASE"]),
    )
    assert response.status_code == 201
    tags = response.json()["tags"]
    assert "uppercase" in tags
    assert "UPPERCASE" not in tags
