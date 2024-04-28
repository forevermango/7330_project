from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr, Field
import mysql.connector
import os
from typing import List, Optional
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
    course_number: str
    number_of_students: int
    year: int
    semester: str
    course_name: str
    has_evaluation: bool = Field(default=False)  # Defaulting to False if not provided

class EvaluationData(BaseModel):
    section_ID: int
    objective_code: int  # Ensure this is included and required
    eval_criteria: str
    eval_A_count: int
    eval_B_count: int
    eval_C_count: int
    eval_F_count: int
    improvements: str

@app.post("/update-evaluation/", response_model=dict)
async def update_evaluation(eval_data: EvaluationData):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        # Check if the objective code exists
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM learning_objectives WHERE code = %s", (eval_data.objective_code,))
        objective = cursor.fetchone()
        if not objective:
            raise HTTPException(status_code=400, detail="Invalid objective code")

        # Proceed with the rest of your logic
        cursor.execute("""
            INSERT INTO course_evaluations (
                section_ID, objective_code, eval_criteria, eval_A_count, eval_B_count, eval_C_count, eval_F_count, improvements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                objective_code=VALUES(objective_code), eval_criteria=VALUES(eval_criteria), eval_A_count=VALUES(eval_A_count), 
                eval_B_count=VALUES(eval_B_count), eval_C_count=VALUES(eval_C_count), eval_F_count=VALUES(eval_F_count), 
                improvements=VALUES(improvements);
        """, (eval_data.section_ID, eval_data.objective_code, eval_data.eval_criteria, eval_data.eval_A_count, eval_data.eval_B_count, 
              eval_data.eval_C_count, eval_data.eval_F_count, eval_data.improvements))
        conn.commit()
        return {"status": "Evaluation updated successfully"}
    finally:
        if conn.is_connected():
            conn.close()

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

@app.get("/sections-by-instructor/", response_model=List[Section])
async def get_sections_by_instructor(instructor_id: int, start_year: int, start_semester: str, end_year: int, end_semester: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT s.section_number, s.number_of_students, s.instructor_id, s.course_number, s.year, s.semester
            FROM sections s
            JOIN semesters sem ON s.year = sem.year AND s.semester = sem.semester
            WHERE s.instructor_id = %s AND
            ((s.year > %s) OR (s.year = %s AND s.semester >= %s)) AND
            ((s.year < %s) OR (s.year = %s AND s.semester <= %s))
            ORDER BY s.year, s.semester;
            """
            cursor.execute(query, (instructor_id, start_year, start_year, start_semester, end_year, end_year, end_semester))
            sections = cursor.fetchall()
            return sections
    finally:
        if conn.is_connected():
            conn.close()

class SectionEvaluation(BaseModel):
    section_number: int
    course_number: str
    number_of_students: int
    year: int
    semester: str
    instructor_id: Optional[int] = None
    evaluation: Optional[EvaluationData] = None


@app.get("/instructor-sections/", response_model=List[SectionEvaluation])
async def get_instructor_sections(instructor_id: int, degree_name: str, year: int, semester: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT s.section_number, s.course_number, s.number_of_students, s.year, s.semester,
               e.eval_ID is not null as has_evaluation
        FROM sections s
        JOIN degree_courses dc ON s.course_number = dc.course_number
        LEFT JOIN course_evaluations e ON s.section_number = e.section_ID
        WHERE s.instructor_id = %s AND dc.degree_name = %s AND s.year = %s AND s.semester = %s
        ORDER BY s.course_number;
        """
        cursor.execute(query, (instructor_id, degree_name, year, semester))
        sections = cursor.fetchall()
        return sections
    finally:
        if conn.is_connected():
            conn.close()


@app.get("/sections-with-evaluations/", response_model=List[SectionEvaluation])
async def get_sections_with_evaluations(instructor_id: int, degree_name: str, year: int, semester: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT s.section_number, s.course_number, s.number_of_students, s.year, s.semester,
                   e.eval_ID, e.eval_criteria, e.eval_A_count, e.eval_B_count, e.eval_C_count, e.eval_F_count, e.improvements
            FROM sections s
            LEFT JOIN course_evaluations e ON s.section_number = e.section_ID
            JOIN degree_courses dc ON s.course_number = dc.course_number
            WHERE s.instructor_id = %s AND dc.degree_name = %s AND s.year = %s AND s.semester = %s
            ORDER BY s.year, s.semester;
            """
            cursor.execute(query, (instructor_id, degree_name, year, semester))
            sections = cursor.fetchall()
            return sections
    finally:
        if conn.is_connected():
            conn.close()

@app.post("/update-evaluation/", response_model=dict)
async def update_evaluation(eval_data: EvaluationData):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        with conn.cursor() as cursor:
            # Update or insert evaluation
            cursor.execute("""
            INSERT INTO course_evaluations (
                section_ID, objective_code, eval_criteria, eval_A_count, eval_B_count, eval_C_count, eval_F_count, improvements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                objective_code=VALUES(objective_code), eval_criteria=VALUES(eval_criteria), eval_A_count=VALUES(eval_A_count), 
                eval_B_count=VALUES(eval_B_count), eval_C_count=VALUES(eval_C_count), eval_F_count=VALUES(eval_F_count), 
                improvements=VALUES(improvements);
            """, (eval_data.section_ID, eval_data.objective_code, eval_data.eval_criteria, eval_data.eval_A_count, eval_data.eval_B_count, 
                  eval_data.eval_C_count, eval_data.eval_F_count, eval_data.improvements))
            conn.commit()
            return {"status": "Evaluation updated successfully"}
    finally:
        if conn.is_connected():
            conn.close()

def duplicate_evaluations(cursor, eval_data):
    # Fetch all associated degrees for the course
    cursor.execute("""
    SELECT degree_name FROM degree_courses WHERE course_number = (SELECT course_number FROM sections WHERE section_number = %s)
    """, (eval_data.section_ID,))
    degrees = cursor.fetchall()
    for degree in degrees:
        if degree['degree_name'] != eval_data.current_degree:
            # Duplicate evaluation data for other degrees
            cursor.execute("""
            INSERT INTO course_evaluations (degree_name, section_ID, eval_criteria, eval_A_count, eval_B_count, eval_C_count, eval_F_count, improvements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                eval_criteria=VALUES(eval_criteria), eval_A_count=VALUES(eval_A_count), eval_B_count=VALUES(eval_B_count),
                eval_C_count=VALUES(eval_C_count), eval_F_count=VALUES(eval_F_count), improvements=VALUES(improvements);
            """, (degree['degree_name'], eval_data.section_ID, eval_data.eval_criteria, eval_data.eval_A_count, eval_data.eval_B_count, eval_data.eval_C_count, eval_data.eval_F_count, eval_data.improvements))
            cursor.commit()


@app.get("/degrees/", response_model=List[DegreeOption])
async def list_degrees():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, level FROM degrees")
        degree_rows = cursor.fetchall()
        return [DegreeOption(name=row['name'], level=row['level']) for row in degree_rows]
    finally:
        if conn.is_connected():
            conn.close()

@app.get("/instructors/", response_model=List[InstructorOption])
async def list_instructors():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT instructor_id, name FROM instructors")
        instructor_rows = cursor.fetchall()
        return [InstructorOption(id=row['instructor_id'], name=row['name']) for row in instructor_rows]
    finally:
        if conn.is_connected():
            conn.close()

@app.get("/semesters/", response_model=List[SemesterOption])
async def list_semesters():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT CONCAT(year, ' ', semester) AS semester_year FROM semesters ORDER BY year, semester")
        semester_rows = cursor.fetchall()
        return [SemesterOption(semester_year=row['semester_year']) for row in semester_rows]
    finally:
        if conn.is_connected():
            conn.close()


@app.get("/sections-by-instructor-degree-semester/", response_model=List[SectionDetails])
async def get_sections_by_instructor_degree_semester(instructor_id: int, degree_name: str, degree_level: str, semester: str, year: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT s.section_number, s.course_number, s.number_of_students, c.name AS course_name, s.year, s.semester,
               e.eval_ID, e.objective_code, e.eval_criteria, e.eval_A_count, e.eval_B_count, e.eval_C_count, e.eval_F_count, e.improvements
        FROM sections s
        JOIN courses c ON s.course_number = c.course_number
        JOIN degree_courses dc ON c.course_number = dc.course_number
        LEFT JOIN course_evaluations e ON s.section_number = e.section_ID
        WHERE s.instructor_id = %s AND dc.degree_name = %s AND dc.degree_level = %s AND s.semester = %s AND s.year = %s
        ORDER BY s.section_number;
        """
        cursor.execute(query, (instructor_id, degree_name, degree_level, semester, year))
        sections = cursor.fetchall()
        return [SectionDetails(**section) for section in sections]
    finally:
        if conn.is_connected():
            conn.close()



@app.get("/sections-with-evaluations/", response_model=List[SectionEvaluation])
async def get_sections_with_evaluations(instructor_id: int, degree_name: str, degree_level: str, year: int, semester: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            query = """
            SELECT s.section_number, s.course_number, s.number_of_students, s.year, s.semester,
                   s.instructor_id, e.eval_ID, e.eval_criteria, e.eval_A_count, e.eval_B_count, 
                   e.eval_C_count, e.eval_F_count, e.improvements
            FROM sections s
            LEFT JOIN course_evaluations e ON s.section_number = e.section_ID
            JOIN degree_courses dc ON s.course_number = dc.course_number
            WHERE s.instructor_id = %s AND dc.degree_name = %s AND dc.degree_level = %s 
                  AND s.year = %s AND s.semester = %s
            ORDER BY s.course_number;
            """
            cursor.execute(query, (instructor_id, degree_name, degree_level, year, semester))
            sections = []
            for row in cursor.fetchall():
                evaluation = {
                    'objective_code': row['eval_ID'],
                    'eval_criteria': row['eval_criteria'],
                    'eval_A_count': row['eval_A_count'],
                    'eval_B_count': row['eval_B_count'],
                    'eval_C_count': row['eval_C_count'],
                    'eval_F_count': row['eval_F_count'],
                    'improvements': row['improvements']
                } if row['eval_ID'] else None
                sections.append({
                    'section_number': row['section_number'],
                    'course_number': row['course_number'],
                    'number_of_students': row['number_of_students'],
                    'year': row['year'],
                    'semester': row['semester'],
                    'instructor_id': row['instructor_id'],
                    'evaluation': evaluation
                })
            return sections
    finally:
        if conn.is_connected():
            conn.close()

