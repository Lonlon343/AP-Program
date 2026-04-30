import requests

URL = "http://127.0.0.1:8000/"  

def test_get_root():
    response = requests.get(URL)
    if response.status_code == 200:
        print("GET / - Status Code: SUCCESS")
    else:
        print("GET failed with Status Code:")


def create_notes():
    for i in range(100):
        payload = {
            "title": "Test Note {i}",
            "content": "This is test note number {i}.",
            "category": "test",
        }
        response = requests.post(URL + "notes/", json=payload)
        if response.status_code == 201:
            print(f"Note {i} created successfully")
        else:
            print(f"Failed to create note {i}")
        print(response.json())

def test_post_creation():
    payload = {
        "title": "title",
        "content": "This is a test note.",
        "category": "test",
        "tags": ["test", "note"]
    }
    response = requests.post(URL + "notes/", json=payload)
    if response.status_code == 201:
        print("POST /notes - Note created successfully")
    else:
        print("POST /notes - Failed to create note")
    print(response.json())

    if response.json()["title"] == payload["title"]:
        print("Note title matches the payload")
    else:
        print("Note title does not match the payload")

def create_note_for_testing():
    payload = {
        "title": "Test Note for GET",
        "content": "This note is created for testing GET requests.",
        "category": "test",
        "tags": ["test", "get"]
    }
    response = requests.post(URL + "notes/", json=payload)
    if response.status_code == 201:
        print("Note created successfully for GET testing")
    else:
        print("Failed to create note for GET testing")  
    return response.json()["id"]



