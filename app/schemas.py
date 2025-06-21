from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    credits: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class CourseRequest(BaseModel):
    topic: str
    language: Optional[str] = "Português"
    depth_level: Optional[str] = "Intermediário"
    voice_tone: Optional[str] = "Formal"
    generate_cover_image: Optional[bool] = True

class CourseContentFinalSummary(BaseModel):
    title: str
    content: str

class CourseContentLesson(BaseModel):
    lesson_title: str
    content: str

class CourseContentPracticeActivity(BaseModel):
    title: str
    content: str

class CourseContentQuizAlternative(BaseModel):
    text: str
    is_correct: bool

class CourseContentQuizQuestion(BaseModel):
    text: str
    alternatives: List[CourseContentQuizAlternative]

class CourseContentModule(BaseModel):
    module_title: str
    chapter: str
    lessons: List[CourseContentLesson]
    practice_activities: List[CourseContentPracticeActivity]

class CourseContent(BaseModel):
    title: str
    subtitle: str
    introduction: str
    wallpaper: str
    modules: List[CourseContentModule]
    final_summary: CourseContentFinalSummary
    assessment_quiz: List[CourseContentQuizQuestion]

class CourseResponse(BaseModel):
    id: int
    title: str
    subtitle: str
    introduction: str
    wallpaper: str
    modules: List[CourseContentModule]
    final_summary: CourseContentFinalSummary
    assessment_quiz: List[CourseContentQuizQuestion]
    language: str
    depth_level: str
    voice_tone: str
    user_id: int

    class Config:
        from_attributes = True

class CourseList(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True