import requests
import pytest


BASE_URL = "http://127.0.0.1:8000"

def test_create_note():
    """Test creating a new note"""
    note_data = {
        "title": "Test Note",
        "content": "Test content",
        "category": "Testing",
        "tags": ["test", "pytest"]
    }
    response = requests.post(
        f"{BASE_URL}/notes", 
        json=note_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Note"
    assert "id" in data
    assert "created_at" in data


def test_list_notes():
    """Test listing all notes"""
    response = requests.get(f"{BASE_URL}/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_note_by_id():
    """Test getting specific note"""
    note_data = {
        "title": "Test Note for Get",
        "content": "Content for get test",
        "category": "Testing",
        "tags": ["get", "test"]
    }
    response = requests.post(f"{BASE_URL}/notes", json=note_data)
    assert response.status_code == 201
    note_id = response.json()["id"]

    response = requests.get(f"{BASE_URL}/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Test Note for Get"


def test_update_note():
    """Test updating a note (PUT)"""
    note_data = {
        "title": "Note to Update",
        "content": "Original content",
        "category": "Testing",
        "tags": ["update", "test"]
    }
    response = requests.post(f"{BASE_URL}/notes", json=note_data)
    assert response.status_code == 201
    note_id = response.json()["id"]

    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Updated",
        "tags": ["updated"]
    }
    response = requests.put(f"{BASE_URL}/notes/{note_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert data["category"] == "Updated"


def test_delete_note():
    """Test deleting a note"""
    # Create then delete
    note_data = {
        "title": "Note to Delete",
        "content": "Content to delete",
        "category": "Testing",
        "tags": ["delete", "test"]
    }
    create_resp = requests.post(f"{BASE_URL}/notes", json=note_data)
    note_id = create_resp.json()["id"]
    
    response = requests.delete(f"{BASE_URL}/notes/{note_id}")
    assert response.status_code in [200, 204]
    
    # Verify it's gone
    get_resp = requests.get(f"{BASE_URL}/notes/{note_id}")
    assert get_resp.status_code == 404


def test_filter_by_category():
    """Test filtering notes by category"""
    # Create notes in specific category
    for i in range(3):
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Work",
            "tags": []
        })
    response = requests.get(f"{BASE_URL}/notes?category=Work")
    assert response.status_code == 200
    


def test_filter_by_tag():
    """Test filtering by tag"""
    for i in range(3):
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Testing",
            "tags": ["important"]
        })
    response = requests.get(f"{BASE_URL}/notes?tag=important")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_combined_filters():
    """Test using multiple filters together"""
    for i in range(5):
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Work",
            "tags": ["important", "urgent"]
        })
    response = requests.get(f"{BASE_URL}/notes?category=Work&tag=important")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_date_filtering():
    """Test date-based filtering (Day 3 Task 5)"""
    # Create notes with specific created_at dates
for i in range(3):  
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Testing",
            "tags": [],
            "created_at": f"2024-06-{10+i}T12:00:00Z"
        })
response = requests.get(f"{BASE_URL}/notes?created_after=2024-06-11T00:00:00Z")
assert response.status_code == 200
data = response.json()
assert isinstance(data, list)   


def test_create_note_missing_field():
    """Test creating note with missing required field"""
    invalid_note = {
        "title": "Test",
        # Missing content and category
    }
    response = requests.post(f"{BASE_URL}/notes", json=invalid_note)
    assert response.status_code == 422


def test_get_nonexistent_note():
    """Test getting a note that doesn't exist"""
    response = requests.get(f"{BASE_URL}/notes/999")
    assert response.status_code == 404

def test_update_nonexistent_note():
    """Test updating a note that doesn't exist"""
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Testing",
        "tags": []
    }
    response = requests.put(f"{BASE_URL}/notes/999", json=update_data)
    assert response.status_code == 404




def test_list_categories():
    """Test GET /categories endpoint (Day 3 Task 3)"""
    response = requests.get(f"{BASE_URL}/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(cat, str) for cat in data)

def test_notes_by_category():
    """Test GET /categories/{category}/notes (Day 3 Task 4)"""
    for i in range(3):
        requests.post(f"{BASE_URL}/notes", json={
            "title": f"Note {i}",
            "content": "Content",
            "category": "Work",
            "tags": []
        })
    response = requests.get(f"{BASE_URL}/categories/Work/notes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(note, dict) for note in data)


def test_notes_statistics():
    """Test GET /notes/stats endpoint (Day 3 Task 2)"""
    response = requests.get(f"{BASE_URL}/notes/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "total_notes" in data
    assert "by_category" in data
    assert "top_tags" in data
    assert "unique_tags_count" in data


def test_patch_note():
    """Test PATCH to update only title (Day 3 Task 4)"""
    note_data = {
        "title": "Note to Patch",
        "content": "Content to patch",
        "category": "Testing",
        "tags": []
    }
    response = requests.post(f"{BASE_URL}/notes", json=note_data)
    assert response.status_code == 201
    note_id = response.json()["id"]

    patch_data = {"title": "Patched Title"}
    response = requests.patch(f"{BASE_URL}/notes/{note_id}", json=patch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Patched Title"
    assert data["content"] == "Content to patch"
    assert data["category"] == "Testing"
    assert data["tags"] == []
    assert "id" in data
    assert "created_at" in data


def test_patch_multiple_fields():
    """Test PATCH with multiple fields"""
    # Similar but update title and content
    pass


#Filtering tests for Day 4

def test_filter_by_search():
    """Test filtering notes by search term"""
    requests.post(f"{BASE_URL}/notes", json={
        "title": "Unique Search Term XYZ",
        "content": "Content",
        "category": "Testing",
        "tags": []
    })
    response = requests.get(f"{BASE_URL}/notes?search=Unique+Search+Term+XYZ")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any("Unique Search Term XYZ" in n["title"] for n in data)


def test_delete_nonexistent_note():
    """Test deleting a note that doesn't exist"""
    response = requests.delete(f"{BASE_URL}/notes/999999")
    assert response.status_code == 404



#Bonus challenges 
def test_list_tags():
    """Test GET /tags returns all unique tags"""
    requests.post(f"{BASE_URL}/notes", json={
        "title": "Tag Test Note",
        "content": "Content",
        "category": "Testing",
        "tags": ["tagtest"]
    })
    response = requests.get(f"{BASE_URL}/tags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(t, str) for t in data)
    assert "tagtest" in data


def test_get_notes_by_tag_endpoint():
    """Test GET /tags/{tag_name}/notes"""
    tag = "endpointtag"
    requests.post(f"{BASE_URL}/notes", json={
        "title": "Tag Endpoint Note",
        "content": "Content",
        "category": "Testing",
        "tags": [tag]
    })
    response = requests.get(f"{BASE_URL}/tags/{tag}/notes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(tag in n["tags"] for n in data)



def test_empty_title():
    """Test creating a note with an empty title"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "",
        "content": "Content",
        "category": "Testing",
        "tags": []
    })
    assert response.status_code in [201, 422]


def test_very_long_content():
    """Test creating a note with very long content"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "Long Content Note",
        "content": "A" * 10000,
        "category": "Testing",
        "tags": []
    })
    assert response.status_code == 201
    assert len(response.json()["content"]) == 10000


def test_special_characters():
    """Test creating a note with special characters in title"""
    title = "Special <chars> & \"quotes\" 'apostrophes'"
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": title,
        "content": "Content with symbols: !@#$%^&*()",
        "category": "Testing",
        "tags": ["special-chars"]
    })
    assert response.status_code == 201
    assert response.json()["title"] == title


def test_unicode_title():
    """Test creating a note with unicode in title"""
    title = "Unicode: \u65e5\u672c\u8a9e \u4e2d\u6587 \u0627\u0644\u0639\u0631\u0628\u064a\u0629"
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": title,
        "content": "Content",
        "category": "Testing",
        "tags": []
    })
    assert response.status_code == 201
    assert response.json()["title"] == title


#3 Test database features 
def test_tag_relationship():
    """Tags created with a note are returned in the note response"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "Relationship Test",
        "content": "Content",
        "category": "Testing",
        "tags": ["rel1", "rel2", "rel3"]
    })
    assert response.status_code == 201
    data = response.json()
    assert set(data["tags"]) == {"rel1", "rel2", "rel3"}


def test_many_to_many_shared_tag():
    """Two notes sharing a tag both appear under that tag"""
    tag = "sharedtag"
    for title in ["Note Alpha", "Note Beta"]:
        requests.post(f"{BASE_URL}/notes", json={
            "title": title, "content": "Content",
            "category": "Testing", "tags": [tag]
        })
    response = requests.get(f"{BASE_URL}/tags/{tag}/notes")
    assert response.status_code == 200
    titles = [n["title"] for n in response.json()]
    assert "Note Alpha" in titles
    assert "Note Beta" in titles


def test_database_persistence():
    """Created note can be retrieved by ID (proves DB write + read)"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": "Persistence Test",
        "content": "Content",
        "category": "Testing",
        "tags": []
    })
    assert response.status_code == 201
    note_id = response.json()["id"]

    response = requests.get(f"{BASE_URL}/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["id"] == note_id


@pytest.mark.parametrize("category", ["Work", "Personal", "Study"])
def test_create_note_various_categories(category):
    """Test that notes can be created in different categories"""
    response = requests.post(f"{BASE_URL}/notes", json={
        "title": f"Note in {category}",
        "content": "Content",
        "category": category,
        "tags": []
    })
    assert response.status_code == 201
    assert response.json()["category"] == category  