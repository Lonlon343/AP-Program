from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path
from sqlmodel import SQLModel, Field, Session, create_engine, Relationship
from typing import Optional
from sqlmodel import select, or_, col


app = FastAPI(
    title="Meine erste FastAPI Anwendung",
    description="Simple note management API built with FastAPI",
    version="1.2.0"
)

from typing import Annotated
from fastapi import Depends

def get_session():
    """Create a new database session for each request"""
    with Session(engine) as session:
        yield session

# Type alias for cleaner code
SessionDep = Annotated[Session, Depends(get_session)]

#Task 6 Step: 4

from pydantic import BaseModel

# API Input model
class NoteCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] = []

# API Output model
class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str]
    created_at: str
    
    class Config:
        from_attributes = True


# Many-to-many link table between Note and Tag
class NoteTagLink(SQLModel, table=True):
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True): # This is the database model for tags (what we store in the database)
    __tablename__ = 'tags'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # Unique tag name

    # Many-to-many relationship with NoteDB via link table
    notes: list["NoteDB"] = Relationship(back_populates="tags", link_model=NoteTagLink)


class NoteDB(SQLModel, table=True): # This is the database model for notes (what we store in the database)
    __tablename__ = 'notes'

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Many-to-many relationship with Tag via link table
    tags: list[Tag] = Relationship(back_populates="notes", link_model=NoteTagLink)


# Create database engine
engine = create_engine("sqlite:///notes.db")

# Create tables (NoteDB, Tag, and NoteTagLink)
SQLModel.metadata.create_all(engine)



@app.get("/") # GET für Abrufen von Daten ohne Parameter
def root():
    return {"Message": "Hi World", "Name": "Leon", "Alter": 29}


@app.get("/name/{name}") # GET für Abrufen von Daten mit Pfad-Parametern
def greet_name(name: str):
    return {"Message": f"Hi {name} !"}

@app.get("/age/{age}") # GET für Abrufen von Daten mit Pfad-Parametern
def tell_age(age: int):
    if age == 1:
        return {"Message": f"Du bist {age} Jahr alt! Du bist minderjährig!"}
    if age < 18:
        return {"Message": f"Du bist {age} Jahre alt! Du bist minderjährig!"}
    if age >= 140:
        raise HTTPException(status_code=400, detail="Ungültiges Alter")
    return {"Message": f"Du bist {age} Jahre alt!"}

@app.get("/add/{num1}/{num2}") # GET für Addition von zwei Zahlen
def add_numbers(num1: int, num2: int):
    summe = num1 + num2
    return {"Message": f"Die Summe von {num1} und {num2} ist {summe}!"}

###############
# Note Api Endpoints Day 2
################

class NoteCreate(BaseModel): # This is the input model for creating a note (what the client sends)
    title: str
    content: str
    category: str
    tags: list[str] = []  # ← ADD THIS (default empty list)



class Note(BaseModel): # This is the internal model used for storing notes in memory
    id: int
    title: str
    content: str
    category: str  # ← ADD THIS
    tags: list[str] = []  # ← ADD THIS
    created_at: str


NOTES_FILE = Path("data/notes.json")  # Define path to JSON file for storing notes

def load_notes():   # for loading notes from JSON file. Returns list of Note objects and next ID counter
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


def save_notes(notes_db):  # Add notes_db as parameter. For save to JSON only
    """Save notes to JSON file after each change"""
    # Ensure data directory exists
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(NOTES_FILE, 'w') as f:
        # Convert Note objects to dicts
        notes_data = [note.dict() for note in notes_db]
        json.dump(notes_data, f, indent=2)



@app.post("/notes", status_code=201)  # POST für Erstellen von Notizen
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Create a new note in database"""
    
    # Create note
    db_note = NoteDB(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    # Get or create tags (case-insensitive, deduplicated)
    tag_objects = []
    seen_tags = set() # To track seen tags and avoid duplicates
    
    # Process tags from input, ensuring case-insensitivity and no duplicates
    for tag_name in note.tags:
        tag_name_lower = tag_name.lower().strip()
        if not tag_name_lower or tag_name_lower in seen_tags:
            continue
        
        seen_tags.add(tag_name_lower)
        
        # Find existing tag or create new one
        statement = select(Tag).where(Tag.name == tag_name_lower)
        existing_tag = session.exec(statement).first()
        
        if existing_tag:
            tag_objects.append(existing_tag)
        else:
            new_tag = Tag(name=tag_name_lower)
            session.add(new_tag)
            tag_objects.append(new_tag)
    
    db_note.tags = tag_objects
    
    session.add(db_note)
    session.commit() 
    session.refresh(db_note)  # Get the generated ID and load relationships
    
    # Convert to response model
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        category=db_note.category,
        tags=[tag.name for tag in db_note.tags],
        created_at=db_note.created_at.isoformat()
    )


@app.get("/notes")  # GET für Abrufen von allen Notizen mit optionalen Filtern
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None
) -> list[NoteResponse]:
    """List notes with filters"""
    
    # Build query
    statement = select(NoteDB)
    
    # Apply filters
    if category:
        statement = statement.where(NoteDB.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(NoteDB.title).ilike(f"%{search_lower}%"),
                col(NoteDB.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(NoteDB.tags).where(Tag.name == tag_lower)
    
    # Execute query
    notes = session.exec(statement).all()
    
    # Convert to response models
    return [
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]


@app.get("/notes/category/{category}")  # GET für Abrufen von Notizen in einer Kategorie
def get_notes_by_category(category: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes in a specific category"""
    statement = select(NoteDB).where(NoteDB.category == category)
    notes = session.exec(statement).all()
    if not notes:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return [
        
        NoteResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            category=n.category,
            tags=[tag.name for tag in n.tags],
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]


@app.get("/notes/stats")  # GET für Statistiken zu Notizen
def get_notes_stats(session: SessionDep):
    statement = select(NoteDB)
    notes = session.exec(statement).all()
    categories = {}
    tag_counts = {}
    unique_tags = set()
    
    for note in notes:
        # Count categories
        categories[note.category] = categories.get(note.category, 0) + 1
        # Count tags
        for tag in note.tags:
            tag_counts[tag.name] = tag_counts.get(tag.name, 0) + 1
            unique_tags.add(tag.name)

    # Sort tags by count
    top_tags = []
    for tag, count in tag_counts.items():
        top_tags.append({"tag": tag, "count": count})
    top_tags.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_notes": len(notes),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": len(unique_tags)
    }


@app.delete("/notes/{note_id}")  # DELETE für Löschen von Notizen
def delete_note(note_id: int, session: SessionDep):
    """Delete a note by ID"""

    note = session.get(NoteDB, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    session.delete(note)
    session.commit()
    return {"message": "Note deleted"}


@app.get("/queryparameters")  # GET für Abrufen von Daten mit Query-Parametern
def query_parameters(param1: str = None, param2: int = None) -> dict:


    namen = ['Leon', 'Lisa', 'Lena', 'Lukas', 'Laura']

    if not param1:
        return {"namen": namen}

    namen_gefiltert = []
    for name in namen:
        if param1 in name:
            namen_gefiltert.append(name)

    return {
        "param1": param1,
        "param2": param2,
        "namen_gefiltert": namen_gefiltert
    }


@app.put("/notes/{note_id}")  # PUT für vollständige Updates (alle Felder müssen gesendet werden)
def update_note(note_id: int, note_update: NoteCreate, session: SessionDep) -> NoteResponse:
    """Update an existing note"""
    
    note = session.get(NoteDB, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note.title = note_update.title
    note.content = note_update.content
    note.category = note_update.category
    
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )



##@app.get("/notes/{note_tag}")  
#def get_note_by_tag(note_tag: str):
 #   """Get a note by searching for a tag in the title or content"""
#
 #   notes_db, _ = load_notes()
  #  for note in notes_db:
   #     if note_tag in note.title or note_tag in note.content:
    #        return note
    
    #raise HTTPException(404, "Note not found")

@app.get("/tags")  # GET für Abrufen von Tags
def list_tags(session: SessionDep) -> list[str]:
    """Get all unique tags from all notes"""
    
    tags = session.exec(select(Tag)).all()  # direkt aus der Tag-Tabelle

    all_tags = set()
    for tag in tags:
        all_tags.add(tag.name)
    
    return sorted(list(all_tags))


@app.get("/tags/{tag_name}/notes") # GET für Abrufen von Notizen mit einem bestimmten Tag
def get_notes_by_tag(tag_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes with a specific tag"""
    
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    notes = session.exec(select(NoteDB).where(NoteDB.tags.any(Tag.name == tag_name))).all()
    
    # Filter notes by tag
    filtered = []
    for note in notes:
        if tag_name in [tag.name for tag in note.tags]:
            filtered.append(NoteResponse(
                id=note.id,
                title=note.title,
                content=note.content,
                category=note.category,
                tags=[tag.name for tag in note.tags],
                created_at=note.created_at.isoformat()
            ))
    
    return filtered


@app.get("/notes/{note_id}")  # GET für Abrufen von note ids
def get_note(note_id:int, session: SessionDep) -> NoteResponse:
    note = session.get(NoteDB, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )


# Task3

@app.get("/categories")  # GET für Abrufen von Kategorien
def list_categories(session: SessionDep) -> list[str]:
    """Get all unique categories from all notes"""
    notes = session.exec(select(NoteDB)).all()
    
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found")
    
    # Collect unique categories
    unique_categories = set()
    for note in notes:
        unique_categories.add(note.category)
    
    # Return sorted list
    return sorted(list(unique_categories))


@app.get("/categories/{category_name}/notes")  # GET für Abrufen von Notizen in einer Kategorie
def get_notes_by_category(category_name: str, session: SessionDep) -> list[NoteResponse]:
    """Get all notes in a specific category"""
    notes = session.exec(select(NoteDB)).all()
    
    # Filter notes by category
    filtered = []
    for note in notes:
        if note.category == category_name:
            filtered.append(NoteResponse(
                id=note.id,
                title=note.title,
                content=note.content,
                category=note.category,
                tags=[tag.name for tag in note.tags],
                created_at=note.created_at.isoformat()
            ))
    
    if not filtered:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return filtered

# Task4

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


@app.patch("/notes/{note_id}")  # PATCH für partielle Updates (nur geänderte Felder)
def partial_update_note(note_id: int, note_update: NoteUpdate, session: SessionDep) -> NoteResponse:
    """
    Partially update a note (only provided fields)
    
    Unlike PUT, PATCH only updates fields you provide
    """
    note = session.get(NoteDB, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Update only provided fields
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    if note_update.category is not None:
        note.category = note_update.category
    if note_update.tags is not None:
        tag_objects = []
        for tag_name in note_update.tags:
            tag_name_lower = tag_name.lower().strip()
            existing_tag = session.exec(select(Tag).where(Tag.name == tag_name_lower)).first()
            if existing_tag:
                tag_objects.append(existing_tag)
            else:
                new_tag = Tag(name=tag_name_lower)
                session.add(new_tag)
                tag_objects.append(new_tag)
        note.tags = tag_objects

    session.add(note)
    session.commit()
    session.refresh(note)

    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        category=note.category,
        tags=[tag.name for tag in note.tags],
        created_at=note.created_at.isoformat()
    )


#Task 6 Step: 5 Update create_note endpoint to use database ^
