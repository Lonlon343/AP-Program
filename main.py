from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import json
from pathlib import Path
from sqlmodel import SQLModel, Field, Session, create_engine, Relationship
from datetime import datetime
from typing import Optional

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
    tags: list[str] = []  # ← ADD THIS (default empty list)



class Note(BaseModel):
    id: int
    title: str
    content: str
    category: str  # ← ADD THIS
    tags: list[str] = []  # ← ADD THIS
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
            tags=note.tags,
            created_at=datetime.now(timezone.utc).isoformat()
        )

        notes_db.append(new_note)  # Add new note to the in-memory list
        save_notes(notes_db)  # Save the updated list to the JSON file
        
        return new_note

@app.get("/notes")
def list_notes(
    category: str = None,
    search: str = None,
    tag: str = None,
    created_after: str = None,
    created_before: str = None
) -> list[Note]:
    """
    List notes with optional filters
    
    - category: Filter by category
    - search: Search in title and content
    - tag: Filter by tag
    """
    notes_db, _ = load_notes()
    
    # Apply filters
    filtered = []
    for note in notes_db:
        # Filter by category
        if category and note.category != category:
            continue
        
        # Filter by search term
        if search:
            search_lower = search.lower()
            title_match = search_lower in note.title.lower()
            content_match = search_lower in note.content.lower()
            if not (title_match or content_match):
                continue
        
        if created_after and note.created_at < created_after:
            continue  # Skip notes created before the threshold

        if created_before and note.created_at > created_before:
            continue  # Skip notes created after the threshold
        
        # Filter by tag
        if tag and tag not in note.tags:
            continue
        
        filtered.append(note)
    
    return filtered


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
    notes_db, _ = load_notes()
    categories = {}
    tag_counts = {}
    unique_tags = set()
    
    for note in notes_db:
        # Count categories
        categories[note.category] = categories.get(note.category, 0) + 1
        # Count tags
        for tag in note.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
            unique_tags.add(tag)

    top_tags = sorted(
        [{"tag": tag, "count": count} for tag, count in tag_counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )
    return {
        "total_notes": len(notes_db),
        "by_category": categories,
        "top_tags": top_tags,
        "unique_tags_count": len(unique_tags)
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


@app.get("/queryparameters")
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


@app.put("/notes/{note_id}")
def update_note(note_id: int, note_update: NoteCreate) -> Note:
    """Update an existing note"""
    
    notes_db, _ = load_notes()
    
    # Find the note
    for i, note in enumerate(notes_db):
        if note.id == note_id:
            # Update note (keep id and created_at)
            updated_note = Note(
                id=note.id,
                title=note_update.title,
                content=note_update.content,
                category=note_update.category,
                tags=note_update.tags,
                created_at=note.created_at
            )
            
            notes_db[i] = updated_note
            save_notes(notes_db)
            return updated_note
    
    # Not found
    raise HTTPException(
        status_code=404,
        detail=f"Note with ID {note_id} not found"
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

@app.get("/tags")
def list_tags() -> list[str]:
    """Get all unique tags from all notes"""
    
    notes_db, _ = load_notes()
    
    # Collect all tags
    all_tags = set()
    for note in notes_db:
        for tag in note.tags:
            all_tags.add(tag)
    
    # Return sorted list
    return sorted(list(all_tags))

@app.get("/tags/{tag_name}/notes")
def get_notes_by_tag(tag_name: str) -> list[Note]:
    """Get all notes with a specific tag"""
    
    notes_db, _ = load_notes()
    
    # Filter notes by tag
    filtered = []
    for note in notes_db:
        if tag_name in note.tags:
            filtered.append(note)
    
    return filtered

# Task3

@app.get("/categories")
def list_categories() -> list[str]:
    """Get all unique categories from all notes"""
    notes_db, _ = load_notes()
    
    # Collect unique categories
    unique_categories = set()
    for note in notes_db:
        unique_categories.add(note.category)
    
    # Return sorted list
    return sorted(list(unique_categories))

@app.get("/categories/{category_name}/notes")
def get_notes_by_category(category_name: str) -> list[Note]:
    """Get all notes in a specific category"""
    notes_db, _ = load_notes()
    
    # Filter notes by category
    filtered = []
    for note in notes_db:
        if note.category == category_name:
            filtered.append(note)
    
    return filtered

# Task4

from typing import Optional

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None

@app.patch("/notes/{note_id}")
def partial_update_note(note_id: int, note_update: NoteUpdate) -> Note:
    """
    Partially update a note (only provided fields)
    
    Unlike PUT, PATCH only updates fields you provide
    """
    notes_db, _ = load_notes()

    for i, note in enumerate(notes_db):
        if note.id == note_id:
            # Update only provided fields
            if note_update.title is not None:
                note.title = note_update.title
            if note_update.content is not None:
                note.content = note_update.content
            if note_update.category is not None:
                note.category = note_update.category
            if note_update.tags is not None:
                note.tags = note_update.tags

            notes_db[i] = note
            save_notes(notes_db)
            return note
    
    raise HTTPException(status_code=404, detail="Note not found")


#Task 6

from sqlmodel import SQLModel, Field, Session, create_engine, Relationship
from datetime import datetime
from typing import Optional


# Many-to-many link table between Note and Tag
class NoteTagLink(SQLModel, table=True):
    note_id: Optional[int] = Field(default=None, foreign_key="notes.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = 'tags'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # Unique tag name

    # Many-to-many relationship with NoteDB via link table
    notes: list["NoteDB"] = Relationship(back_populates="tags", link_model=NoteTagLink)


class NoteDB(SQLModel, table=True):
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


#Task 6 Step: 3

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


#Task 6 Step: 5 Update create_note endpoint to use database

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate, session: SessionDep) -> NoteResponse:
    """Create a new note in database"""
    
    # Create note
    db_note = Note(
        title=note.title,
        content=note.content,
        category=note.category
    )
    
    # Get or create tags (case-insensitive, deduplicated)
    tag_objects = []
    seen_tags = set()
    
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



#Task 6 Step: 6 Update List endpoints

from sqlmodel import select, or_, col

@app.get("/notes")
def list_notes(
    session: SessionDep,
    category: str = None,
    search: str = None,
    tag: str = None
) -> list[NoteResponse]:
    """List notes with filters"""
    
    # Build query
    statement = select(Note)
    
    # Apply filters
    if category:
        statement = statement.where(Note.category == category)
    
    if search:
        search_lower = search.lower()
        statement = statement.where(
            or_(
                col(Note.title).ilike(f"%{search_lower}%"),
                col(Note.content).ilike(f"%{search_lower}%")
            )
        )
    
    if tag:
        tag_lower = tag.lower()
        statement = statement.join(Note.tags).where(Tag.name == tag_lower)
    
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


#Task 6: Step 7 - Update Other Endpoints


    

    