from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from auth import router as auth_router
from projects import router as project_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth")
app.include_router(project_router, prefix="/projects")

@app.get("/")
def home():
    return {"message": "AI Project Mentor Backend is Running!"}

@app.get("/test-db")
def test_database():
    try:
        connection = engine.connect()
        connection.close()
        return {"message": "PostgreSQL Connected Successfully!"}
    except Exception as e:
        return {"error": str(e)}