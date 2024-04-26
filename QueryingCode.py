import mysql.connector
from fastapi import FastAPI, Query
from typing import List
from datetime import date
from pydantic import BaseModel

app = FastAPI()

class DegreeID(BaseModel):
    degree_id: str

class DegreeIDStartDateEndDate(BaseModel):
    degree_id: str
    start_date: date
    end_date: date

class ObjectiveCodes(BaseModel):
    objective_codes: List[str]

class CourseNumberStartSemesterEndSemester(BaseModel):
    course_number: str
    start_semester: int
    end_semester: int

class InstructorNameStartSemesterEndSemester(BaseModel):
    instructor_name: str
    start_semester: int
    end_semester: int

# connect to the database
def connect_to_database():
    return mysql.connector.connect(
        host='sql5.freesqldatabase.com',
        user='sql5700157',
        password='IX8Ke7RipR',
        database='sql5700157',
        port=3306
    )

@app.get("/courses/", status_code=200, summary="Get courses by degree", response_description="List of courses retrieved successfully")
def get_courses_by_degree(degree_id: DegreeID):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = """
    SELECT dc.course_number, c.name AS course_name, dc.core_course
    FROM degree_courses dc
    JOIN courses c ON dc.course_number = c.course_number
    JOIN degrees d ON dc.degree_ID = d.name_level
    WHERE d.name_level= %s;
    """
    cursor.execute(query, (degree_id,))
    courses = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return courses

@app.get("/sections/", status_code=200, summary="Get sections by degree and time range", response_description="List of sections retrieved successfully")
def get_sections_by_degree_in_time_range(info: DegreeIDStartDateEndDate):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = """
    SELECT s.section_number, s.semester_year
    FROM sections s
    JOIN semester sem ON s.semester_year = sem.semester_year
    JOIN degree_courses dc ON s.course_number = dc.course_number
    WHERE dc.degree_ID = %s
    AND sem.year BETWEEN %s AND %s
    ORDER BY sem.year, sem.semester;
    """
    cursor.execute(query, (degree_id, start_date, end_date))
    sections = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sections

@app.get("/objectives/", status_code=200, summary="Get objectives by degree", response_description="List of objectives retrieved successfully")
def get_objectives_by_degree(degree_id: DegreeID):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = """
    SELECT lo.code, lo.title, lo.description
    FROM degree_courses dc
    JOIN course_learning_objective clo ON dc.course_number = clo.course_number
    JOIN learning_objectives lo ON clo.code = lo.code
    WHERE dc.degree_ID = %s
    """
    cursor.execute(query, (degree_id,))
    objectives = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return objectives


@app.post("/courses_for_objectives/", status_code=200, summary="List courses for objectives", response_description="List of courses for objectives retrieved successfully")
def list_courses_for_objectives(objective_codes: ObjectiveCodes = Query(..., description="List of objective codes")):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    courses_for_objectives = []
    
    for code in objective_codes.objective_codes:
        query = """
        SELECT c.course_number, c.name
        FROM course_learning_objective clo
        JOIN courses c ON clo.course_number = c.course_number
        WHERE clo.code = %s
        """
        cursor.execute(query, (code,))
        courses = cursor.fetchall()
        courses_for_objectives.extend(courses)
    
    cursor.close()
    connection.close()
    
    return courses_for_objectives

@app.get("/sections_for_course/", status_code=200, summary="Get sections for course", response_description="List of sections for course retrieved successfully")
def list_sections_for_course(course_info: CourseNumberStartSemesterEndSemester):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = """
    SELECT s.section_number, s.semester_year
    FROM sections s
    JOIN semester sem ON s.semester_year = sem.semester_year
    WHERE s.course_number = %s AND sem.year BETWEEN %s AND %s
    """
    cursor.execute(query, (course_info.course_number, course_info.start_semester, course_info.end_semester))
    sections = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sections

@app.get("/sections_for_instructor/", status_code=200, summary="Get sections for instructor", response_description="List of sections for instructor retrieved successfully")
def list_sections_for_instructor(instructor_info: InstructorNameStartSemesterEndSemester):
    connection = connect_to_database()
    cursor = connection.cursor()
    
    query = """
    SELECT s.section_number, s.course_number
    FROM sections s
    JOIN semester sem ON s.semester_year= sem.semester_year
    JOIN instructor i ON s.instructor_id = i.instructor_id
    WHERE i.name = %s AND sem.year BETWEEN %s AND %s
    """
    cursor.execute(query, (instructor_info.instructor_name, instructor_info.start_semester, instructor_info.end_semester))
    sections = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return sections
