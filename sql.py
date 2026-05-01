from sqlmodel import SQLModel, Field, Session, create_engine, Relationship
from datetime import datetime
from typing import Optional

class Note(SQLModel, table=True):
    __tablename__ = 'notes'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Many-to-many relationship with Tag (implicit link table)
    tags: list["Tag"] = Relationship(back_populates="notes")

    class Tag(SQLModel, table=True):
        __tablename__ = 'tags'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)  # Unique tag name
    
    # Many-to-many relationship with Note (implicit link table)
    notes: list[Note] = Relationship(back_populates="tags")

# Create database engine
engine = create_engine("sqlite:///notes.db")

# Create tables (Note, Tag, and link table)
SQLModel.metadata.create_all(engine)