from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

def load_config(file_path):
    """Load configuration from a text file into environment variables."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"An error occurred while reading the configuration file: {e}")

load_config('config.txt')

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db = os.getenv('DATABASE')

class Degree(BaseModel):
    name: str
    level: str

class Course(BaseModel):
    course_number: str
    name: str

class Instructor(BaseModel):
    instructor_id: int
    name: str

class Section(BaseModel):
    section_number: int
    number_of_students: int
    instructor_id: int
    course_number: str
    semester_id: str

class LearningObjective(BaseModel):
    code: int
    title: str
    description: str

@app.post("/add-degree/", status_code=201, summary="Add a new degree", response_description="Degree added successfully")
async def add_degree(degree: Degree):
    return await add_entity(degree, "degree", ("name", "level"))

@app.post("/add-course/", status_code=201, summary="Add a new course", response_description="Course added successfully")
async def add_course(course: Course):
    return await add_entity(course, "courses", ("course_number", "name"))

@app.post("/add-instructor/", status_code=201, summary="Add a new instructor", response_description="Instructor added successfully")
async def add_instructor(instructor: Instructor):
    return await add_entity(instructor, "instructor", ("instructor_id", "name"))

@app.post("/add-section/", status_code=201, summary="Add a new section", response_description="Section added successfully")
async def add_section(section: Section):
    return await add_entity(section, "sections", ("section_number", "number_of_students", "instructor_id", "course_number", "semester_id"))

@app.post("/add-learning-objective/", status_code=201, summary="Add a new learning objective", response_description="Learning objective added successfully")
async def add_learning_objective(learning_objective: LearningObjective):
    return await add_entity(learning_objective, "learning_objectives", ("code", "title", "description"))

async def add_entity(entity, table, columns):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor() as cursor:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            values = tuple(getattr(entity, col) for col in columns)
            query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            return {"status": f"{table[:-1]} added"}  # Removes 's' from table name for the status message
    except mysql.connector.Error as error:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        conn.close()

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user=db_user,
            passwd=db_password,
            database=db
        )
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None

