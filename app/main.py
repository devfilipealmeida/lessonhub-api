from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .routes import auth, users, courses
from .database import engine, Base
from .middleware import rate_limit_middleware
import os
from dotenv import load_dotenv
import time

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LessonHub API",
    description="API para geração de cursos online",
    version="1.0.0"
)

# Middleware de rate limiting
app.middleware("http")(rate_limit_middleware)

# Configuração do CORS para aceitar tudo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para hosts confiáveis (opcional, para produção)
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["*"]
# )

# Middleware para logging de performance
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}