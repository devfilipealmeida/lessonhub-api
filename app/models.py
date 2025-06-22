from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    credits = Column(Integer, default=3)
    
    # Relacionamento com cursos
    courses = relationship("Course", back_populates="user")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    subtitle = Column(String)
    wallpaper = Column(String)
    modules = Column(JSON)  # Armazena a estrutura dos módulos como JSON
    final_summary = Column(JSON)  # Armazena o resumo final como JSON
    assessment_quiz = Column(JSON)  # Armazena o questionário como JSON
    language = Column(String)
    depth_level = Column(String)
    voice_tone = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relacionamento com usuário
    user = relationship("User", back_populates="courses")