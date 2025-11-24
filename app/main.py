from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import Base

from fastapi import Depends, HTTPException, status, Response 
from sqlalchemy.orm import Session 
from sqlalchemy import select 
from sqlalchemy.exc import IntegrityError 
from sqlalchemy.orm import selectinload 
from app.database import SessionLocal 
from app.models import CourseDB
from app.schemas import ( CourseCreate, CourseRead ) 

#Replacing @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) 
    yield

app = FastAPI(lifespan=lifespan)
# CORS (add this block)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # dev-friendly; tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine),

def get_db(): 
    db = SessionLocal() 
    try: 
        yield db 
    finally: 
        db.close() 
 
def commit_or_rollback(db: Session, error_msg: str): 
    try: 
        db.commit() 
    except IntegrityError: 
        db.rollback() 
        raise HTTPException(status_code=409, detail=error_msg) 
 
@app.get("/health") 
def health(): 
    return {"status": "ok"} 
 
#Courses
@app.post("/api/courses", response_model=CourseRead, status_code=201, summary="Create new course") 
def create_course(payload: CourseCreate, db: Session = Depends(get_db)): 
    db_course = CourseDB(**payload.model_dump()) 
    db.add(db_course) 
    commit_or_rollback(db, "Course create failed") 
    db.refresh(db_course) 
    return db_course 
 
@app.get("/api/courses", response_model=list[CourseRead]) 
def list_courses(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)): 
    stmt = select(CourseDB).order_by(CourseDB.id).limit(limit).offset(offset) 
    return db.execute(stmt).scalars().all() 
 

@app.get(
    "/api/courses/{course_id}",response_model=CourseRead,summary="Get a single course",)
def get_course(course_id: int,db: Session = Depends(get_db),):
    course = db.get(CourseDB, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put(
    "/api/courses/{course_id}",response_model=CourseRead,summary="Update an existing course",)
def update_course(course_id: int,payload: CourseCreate,db: Session = Depends(get_db),):
    course = db.get(CourseDB, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.code = payload.code
    course.name = payload.name
    course.credits = payload.credits

    commit_or_rollback(db, "Course update failed")
    db.refresh(course)
    return course

@app.delete("/api/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int,db: Session = Depends(get_db),) -> Response:
    course = db.get(CourseDB, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)