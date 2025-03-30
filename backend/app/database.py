from sqlalchemy import create_engine, Column, Integer, String, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import os
import json
import hashlib

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class BaseEmbedding(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    vector = Column(Vector)  # Dimension will be set in subclasses
    extra_metadata = Column(String, nullable=True)

    def set_metadata(self, metadata_dict):
        """Convert metadata dict to JSON string for storage"""
        self.extra_metadata = json.dumps(metadata_dict) if metadata_dict else None

    def get_metadata(self):
        """Convert stored JSON string back to dict"""
        return json.loads(self.extra_metadata) if self.extra_metadata else None


class ADAEmbedding(BaseEmbedding):
    __tablename__ = "embeddings_ada"
    vector = Column(Vector(768))  # Specific dimension for ADA embeddings


class E5Embedding(BaseEmbedding):
    __tablename__ = "embeddings_e5"

    vector = Column(Vector(384))  # Specific dimension for E5 embeddings
    text_hash = Column(String, unique=True, index=True)
    source_document = Column(String, nullable=True)

    def __init__(self, *args, **kwargs):
        if "text" in kwargs:
            # Generate hash before calling parent constructor
            kwargs["text_hash"] = hashlib.md5(kwargs["text"].encode()).hexdigest()
        super().__init__(*args, **kwargs)


class TestEmbedding(BaseEmbedding):
    __tablename__ = "embeddings_test"
    vector = Column(Vector(3))  # Small dimension for testing


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    response = Column(String, nullable=False)
    context_chunks = Column(JSON, nullable=True)
    similarity_scores = Column(JSON, nullable=True)
    timestamp = Column(String, nullable=False)
    conversation_id = Column(String, nullable=False, index=True)
    conversation_metadata = Column(JSON, nullable=True)

    def set_metadata(self, metadata_dict):
        """Convert metadata dict to JSON string for storage"""
        self.conversation_metadata = metadata_dict if metadata_dict else None

    def get_metadata(self):
        """Get metadata dict"""
        return self.conversation_metadata


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
