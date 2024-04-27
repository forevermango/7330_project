from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr
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
    name: str
    department_code: constr(min_length=2, max_length=4)
    course_code: int  # Ensure within the valid range (1000 to 9999)

    class Config:
        orm_mode = True

class Instructor(BaseModel):
    instructor_id: int
    name: str

class Section(BaseModel):
    section_number: int
    number_of_students: int
    instructor_id: int
    course_number: str
    year: int
    semester: str

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
    # Validate course_code range
    if not (1000 <= course.course_code <= 9999):
        raise HTTPException(status_code=400, detail="Course code must be between 1000 and 9999.")

    # Use add_entity to insert the course into the database
    try:
        response = await add_entity(course, "courses", ("name", "department_code", "course_code"))
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add-instructor/", status_code=201, summary="Add a new instructor", response_description="Instructor added successfully")
async def add_instructor(instructor: Instructor):
    return await add_entity(instructor, "instructors", ("instructor_id", "name"))

@app.post("/add-section/", status_code=201, summary="Add a new section", response_description="Section added successfully")
async def add_section(section: Section):
    return await add_entity(section, "sections", ("section_number", "number_of_students", "instructor_id", "course_number", "year", "semester"))

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
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor
        logging.debug("Fetching degrees from database.")
        cursor.execute("SELECT name, level FROM degrees")
        degree_rows = cursor.fetchall()
        degrees = [DegreeOption(name=row['name'], level=row['level']) for row in degree_rows]

        logging.debug("Fetching semesters from database.")
        cursor.execute("SELECT CONCAT(year, ' ', semester) AS semester_year FROM semesters ORDER BY year, semester")
        semester_rows = cursor.fetchall()
        semesters = [row['semester_year'] for row in semester_rows]

        logging.debug("Fetching instructors from database.")
        cursor.execute("SELECT instructor_id, name FROM instructors")
        instructor_rows = cursor.fetchall()
        instructors = [InstructorOption(id=row['instructor_id'], name=row['name']) for row in instructor_rows]

        return AvailableOptions(degrees=degrees, semesters=semesters, instructors=instructors)
    except Exception as e:
        logging.error(f"Error processing available options: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


class AssociateCourseWithDegree(BaseModel):
    degree_name: str
    degree_level: str
    course_number: str
    core_course: bool

@app.post("/associate-course-with-degree/", status_code=status.HTTP_201_CREATED, summary="Associate a course with a degree", response_description="Course associated with degree successfully")
async def associate_course_with_degree(association: AssociateCourseWithDegree):
    """Associates a course with a degree in the database."""
    # Connect to the database
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor() as cursor:
            # Prepare the SQL query to insert the new association
            query = """
            INSERT INTO degree_courses (degree_name, degree_level, course_number, core_course)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                core_course = VALUES(core_course);
            """
            values = (association.degree_name, association.degree_level, association.course_number, association.core_course)

            # Execute the query
            cursor.execute(query, values)
            conn.commit()
            return {"message": "Course associated with degree successfully."}

    except mysql.connector.Error as error:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        if conn.is_connected():
            conn.close()

class CourseResponse(BaseModel):
    course_number: str
    course_name: str
    is_core_course: bool


@app.get("/courses-by-degree/", response_model=List[CourseResponse], status_code=200, summary="Get courses by degree", response_description="List of courses for a specific degree")
async def get_courses_by_degree(degree_name: str = Query(..., description="The name of the degree"), degree_level: str = Query(..., description="The level of the degree (e.g., Bachelor, Master)")):
    """Fetches courses associated with a specific degree from the database."""
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor(dictionary=True) as cursor:
            # Query to fetch courses associated with a specific degree
            query = """
            SELECT c.course_number, c.name AS course_name, dc.core_course AS is_core_course
            FROM courses c
            JOIN degree_courses dc ON c.course_number = dc.course_number
            WHERE dc.degree_name = %s AND dc.degree_level = %s;
            """
            cursor.execute(query, (degree_name, degree_level))
            courses = cursor.fetchall()
            if not courses:
                raise HTTPException(status_code=404, detail="No courses found for the specified degree")
            return [CourseResponse(**course) for course in courses]

    except mysql.connector.Error as error:
        raise HTTPException(status_code=400, detail=f"Database query error: {str(error)}")
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.get("/list-sections/", response_model=List[Section])
async def list_sections(
    start_year: int = Query(..., description="Start year of the query range"),
    start_semester: str = Query(..., description="Start semester of the query range"),
    end_year: int = Query(..., description="End year of the query range"),
    end_semester: str = Query(..., description="End semester of the query range")):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.section_number, s.number_of_students, s.instructor_id, s.course_number, sem.year, sem.semester
            FROM sections s
            JOIN semesters sem ON s.year = sem.year AND s.semester = sem.semester
            JOIN semester_sort_order so ON sem.semester = so.semester
            WHERE (sem.year > %s OR (sem.year = %s AND so.sort_order >= (SELECT sort_order FROM semester_sort_order WHERE semester = %s)))
              AND (sem.year < %s OR (sem.year = %s AND so.sort_order <= (SELECT sort_order FROM semester_sort_order WHERE semester = %s)))
            ORDER BY sem.year, so.sort_order
        """, (start_year, start_year, start_semester, end_year, end_year, end_semester))
        sections = cursor.fetchall()
        return [Section(**section) for section in sections]
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/learning-objectives/", response_model=List[LearningObjective])
async def list_learning_objectives():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT code, title, description FROM learning_objectives")
        objectives = cursor.fetchall()
        return [LearningObjective(**obj) for obj in objectives]
    finally:
        if conn.is_connected():
            conn.close()

@app.post("/associate-course-objective/", status_code=201, summary="Associate a course with a learning objective", response_description="Association created successfully")
async def associate_course_objective(association: CourseObjectiveAssociation):
    return await add_entity(association, "course_learning_objectives", ("course_number", "objective_code"))

@app.get("/courses-by-objective/", response_model=List[CourseResponse])
async def get_courses_by_objective(objective_codes: List[int] = Query(..., description="List of objective codes")):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            format_strings = ','.join(['%s'] * len(objective_codes))
            query = """
            SELECT c.course_number, c.name AS course_name, COALESCE(dc.core_course, False) AS is_core_course
            FROM courses c
            LEFT JOIN degree_courses dc ON c.course_number = dc.course_number
            JOIN course_learning_objectives clo ON c.course_number = clo.course_number
            WHERE clo.objective_code IN (%s)
            """
            cursor.execute(query % format_strings, tuple(objective_codes))
            courses = cursor.fetchall()
            if not courses:
                raise HTTPException(status_code=404, detail="No courses found for the specified objectives")
            return [CourseResponse(**course) for course in courses]
    finally:
        if conn.is_connected():
            conn.close()

@app.get("/sections-by-course/", response_model=List[Section])
async def get_sections_by_course(course_number: str, start_year: int, start_semester: str, end_year: int, end_semester: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT s.section_number, s.number_of_students, s.instructor_id, s.course_number, s.year, s.semester
            FROM sections s
            WHERE s.course_number = %s AND
            ((s.year > %s) OR (s.year = %s AND s.semester >= %s)) AND
            ((s.year < %s) OR (s.year = %s AND s.semester <= %s))
            ORDER BY s.year, s.semester;
            """
            cursor.execute(query, (course_number, start_year, start_year, start_semester, end_year, end_year, end_semester))
            sections = cursor.fetchall()
            return sections
    finally:
        if conn.is_connected():
            conn.close()
