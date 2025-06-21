from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, courses
from .database import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS para aceitar tudo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(courses.router, prefix="/api")

@app.get("/api/")
def root():
    return {"message": "Hello World"}