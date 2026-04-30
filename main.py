from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path

app = FastAPI(
    title="Meine erste FastAPI Anwendung",
    description="Simple note management API built with FastAPI",
    version="1.2.0"
)


@app.get("/")
def root():
    return {"Message": "Hi World", "Name": "Leon", "Alter": 29}


@app.get("/name/{name}")
def greet_name(name: str):
    return {"Message": f"Hi {name} !"}

@app.get("/age/{age}")
def tell_age(age: int):
    if age == 1:
        return {"Message": f"Du bist {age} Jahr alt! Du bist minderjährig!"}
    if age < 18:
        return {"Message": f"Du bist {age} Jahre alt! Du bist minderjährig!"}
    if age >= 140:
        raise HTTPException(status_code=400, detail="Ungültiges Alter")
    return {"Message": f"Du bist {age} Jahre alt!"}

@app.get("/add/{num1}/{num2}")
def add_numbers(num1: int, num2: int):
    summe = num1 + num2
    return {"Message": f"Die Summe von {num1} und {num2} ist {summe}!"}

###############
# Note Api Endpoints Day 2
################

class NoteCreate(BaseModel):
    title: str
    content: str
    category: str


class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str  # ← ADD THIS
    created_at: str


NOTES_FILE = Path("data/notes.json")  # Define path to JSON file for storing notes

def load_notes():  
    """Load notes from JSON file and return notes list and next ID counter""" 
    notes_db = []  # Initialize empty notes list
    note_id_counter = 1  # Initialize ID counter to 1

    if NOTES_FILE.exists(): # Check if the JSON file exists
        with open(NOTES_FILE, 'r') as f: # Open the file for reading
            content = f.read()
            if not content.strip():
                return notes_db, note_id_counter
            data = json.loads(content)   # Load the JSON data into a Python list
            notes_db = [Note(**note) for note in data]  # Convert each dict in the list to a Note object

            # Set counter to max ID + 1
            if notes_db:
                note_id_counter = max(note.id for note in notes_db) + 1

    return notes_db, note_id_counter


def save_notes(notes_db):
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)


@app.post("/notes", status_code=201)

def create_note(note: NoteCreate) -> Note:
        """Create a new note"""
        
        notes_db, notes_id_counter = load_notes()
        
        new_note = Note(
            id=notes_id_counter,
            title=note.title,
            content=note.content,
            category=note.category,
            created_at=datetime.now(timezone.utc).isoformat()
        )

        notes_db.append(new_note)  # Add new note to the in-memory list
        save_notes(notes_db)  # Save the updated list to the JSON file
        
        return new_note

@app.get("/notes")
def list_notes() -> list[Note]:
    """List all notes"""
    notes_db, _ = load_notes()  # Load notes from JSON file
    return notes_db  # Return the list of Note objects



@app.get("/notes/category/{category}")
def get_notes_by_category(category: str):
    """Get all notes in a specific category"""
    notes_db, _ = load_notes()  # Load notes from JSON file
    filtered_notes = []
    
    for note in notes_db:
        if note.category == category:
            filtered_notes.append(note)
    
    return filtered_notes

@app.get("/notes/stats")
def get_notes_stats():
    """Get statistics about notes"""
    
    notes_db, _ = load_notes()  # Load notes from JSON file
    
    # Count by category
    categories = {}
    for note in notes_db:
        if note.category in categories:
            categories[note.category] += 1
        else:
            categories[note.category] = 1
    
    return {
        "total_notes": len(notes_db),
        "by_category": categories
    }

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a note by ID"""

    notes_db, _ = load_notes()
    
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            notes_db.pop(i)
            save_notes(notes_db)
            return {"message": "Note deleted"}
    
    raise HTTPException(404, "Note not found")

#######################
# DAY 3 
#######################

#CRUD - Create, Read, Update, Delete

@app.get("/queryparameters")
def query_parameters(param1: str = None, param2: int = None) -> dict:

    namen = ['Leon', 'Lisa', 'Lena', 'Lukas', 'Laura']


    if not param1:
        return {"namen":namen} 
    

    namen_gefiltert = []
    for name in namen:
        if param1 in name:
            namen_gefiltert.append(name) 



    return {"param1": param1, 
            "param2": param2,
            "namen_gefiltert": namen_gefiltert
            }

"""query demonstration:"""


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteCreate) -> Note:
    """Update a note by ID"""

    notes_db, _ = load_notes()
    
    for i, existing_note in enumerate(notes_db):
        if existing_note.id == note_id:
            notes_db[i] = Note(
                id=note_id,
                title=note.title,
                content=note.content,
                category=note.category,
                created_at=existing_note.created_at)
            
            save_notes(notes_db)
            return notes_db[i]
        raise HTTPException(404, "Note not found")

##@app.get("/notes/{note_tag}")  
#def get_note_by_tag(note_tag: str):
 #   """Get a note by searching for a tag in the title or content"""
#
 #   notes_db, _ = load_notes()
  #  for note in notes_db:
   #     if note_tag in note.title or note_tag in note.content:
    #        return note
    
    #raise HTTPException(404, "Note not found")

