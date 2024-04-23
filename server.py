from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
from typing import List
import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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
    semester_year: str

class LearningObjective(BaseModel):
    code: int
    title: str
    description: str

class CourseObjectiveAssociation(BaseModel):
    course_number: str
    objective_code: int

class CourseSectionAssociation(BaseModel):
    course_number: str
    section_number: int
    semester_year: str

@app.post("/add-degree/", status_code=201, summary="Add a new degree", response_description="Degree added successfully")
async def add_degree(degree: Degree):
    return await add_entity(degree, "degrees", ("name", "level"))

@app.post("/add-course/", status_code=201, summary="Add a new course", response_description="Course added successfully")
async def add_course(course: Course):
    return await add_entity(course, "courses", ("course_number", "name"))

@app.post("/add-instructor/", status_code=201, summary="Add a new instructor", response_description="Instructor added successfully")
async def add_instructor(instructor: Instructor):
    return await add_entity(instructor, "instructors", ("instructor_id", "name"))

@app.post("/add-section/", status_code=201, summary="Add a new section", response_description="Section added successfully")
async def add_section(section: Section):
    return await add_entity(section, "sections", ("section_number", "number_of_students", "instructor_id", "course_number", "semester_year"))

@app.post("/add-learning-objective/", status_code=201, summary="Add a new learning objective", response_description="Learning objective added successfully")
async def add_learning_objective(learning_objective: LearningObjective):
    return await add_entity(learning_objective, "learning_objectives", ("code", "title", "description"))

@app.post("/associate-course-objective/", status_code=201, summary="Associate a course with a learning objective", response_description="Association created successfully")
async def associate_course_objective(association: CourseObjectiveAssociation):
    return await add_entity(association, "course_learning_objectives", ("course_number", "objective_code"))

@app.post("/associate-course-section/", status_code=201, summary="Associate a course with a section for a specific semester", response_description="Association created successfully")
async def associate_course_section(association: CourseSectionAssociation):
    return await add_entity(association, "sections_courses", ("course_number", "section_number", "semester_year"))

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

# Define the Pydantic models for responses and request bodies
class AvailableOptions(BaseModel):
    degrees: List[tuple]
    semesters: List[str]
    instructors: List[tuple]

class SectionDetails(BaseModel):
    section_number: int
    course_name: str
    course_number: str
    number_of_students: int

class EvaluationData(BaseModel):
    section_id: int
    eval_criteria: str
    eval_a_count: int
    eval_b_count: int
    eval_c_count: int
    eval_f_count: int
    improvements: str

@app.post("/update-evaluation/", status_code=201, summary="Update evaluation data", response_description="Evaluation updated successfully")
async def update_evaluation(eval_data: EvaluationData):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Check if evaluation exists
    cursor.execute("SELECT * FROM course_evaluations WHERE section_ID = %s", (eval_data.section_id,))
    existing_data = cursor.fetchone()
    if existing_data:
        # Update existing evaluation
        cursor.execute("""
            UPDATE course_evaluation SET eval_criteria = %s, eval_A_count = %s, eval_B_count = %s, eval_C_count = %s, eval_F_count = %s, improvements = %s
            WHERE section_ID = %s
            """, (eval_data.eval_criteria, eval_data.eval_a_count, eval_data.eval_b_count, eval_data.eval_c_count, eval_data.eval_f_count, eval_data.improvements, eval_data.section_id))
    else:
        # Insert new evaluation
        cursor.execute("""
            INSERT INTO course_evaluations (section_ID, eval_criteria, eval_A_count, eval_B_count, eval_C_count, eval_F_count, improvements)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (eval_data.section_id, eval_data.eval_criteria, eval_data.eval_a_count, eval_data.eval_b_count, eval_data.eval_c_count, eval_data.eval_f_count, eval_data.improvements))
    conn.commit()
    conn.close()
    return {"status": "Evaluation updated successfully"}

class DegreeOption(BaseModel):
    name: str
    level: str

class SemesterOption(BaseModel):
    semester_year: str

class InstructorOption(BaseModel):
    id: int
    name: str

class AvailableOptions(BaseModel):
    degrees: List[DegreeOption]
    semesters: List[str]
    instructors: List[InstructorOption]

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db
        )
        logging.info("Database connection successful")
        return connection
    except mysql.connector.Error as e:
        logging.error(f"Database connection failed: {e}")
        return None

@app.get("/available-options/", response_model=AvailableOptions)
async def available_options():
    conn = get_db_connection()
    if not conn:
        logging.error("Failed to connect to the database.")
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        cursor = conn.cursor()
        logging.debug("Fetching degrees from database.")
        cursor.execute("SELECT name, level FROM degrees")
        degree_rows = cursor.fetchall()
        degrees = [DegreeOption(name=name, level=level) for name, level in degree_rows]
        logging.debug(f"Degrees fetched: {degrees}")

        logging.debug("Fetching semesters from database.")
        cursor.execute("SELECT DISTINCT semester_year FROM semesters")
        semester_rows = cursor.fetchall()
        semesters = [row[0] for row in semester_rows]
        logging.debug(f"Semesters fetched: {semesters}")

        logging.debug("Fetching instructors from database.")
        cursor.execute("SELECT instructor_id, name FROM instructors")
        instructor_rows = cursor.fetchall()
        instructors = [InstructorOption(id=id, name=name) for id, name in instructor_rows]
        logging.debug(f"Instructors fetched: {instructors}")

        return AvailableOptions(degrees=degrees, semesters=semesters, instructors=instructors)
    except Exception as e:
        logging.error(f"Error processing available options: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
