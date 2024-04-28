from fastapi import APIRouter, HTTPException, Depends, Query
from models import (Degree, Course, Instructor, Section, LearningObjective, 
                    CourseObjectiveAssociation, CourseSectionAssociation, EvaluationData, 
                    SectionDetails, DegreeOption, InstructorOption, Semester, CourseResponse,
                    SectionEvaluation, SectionEvaluationDetail, AssociateCourseWithDegree)
from database import get_db_connection, add_entity
from typing import List

router = APIRouter()

@router.post("/add-degree/", status_code=201, summary="Add a new degree", response_description="Degree added successfully")
async def add_degree(degree: Degree):
    return await add_entity(degree, "degrees", ("name", "level"))

@router.post("/add-course/", status_code=201, summary="Add a new course", response_description="Course added successfully")
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


@router.post("/add-instructor/", status_code=201, summary="Add a new instructor", response_description="Instructor added successfully")
async def add_instructor(instructor: Instructor):
    return await add_entity(instructor, "instructors", ("instructor_id", "name"))

@router.post("/add-section/", status_code=201, summary="Add a new section", response_description="Section added successfully")
async def add_section(section: Section):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        # Check if the semester exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM semesters WHERE year = %s AND semester = %s", (section.year, section.semester))
            result = cursor.fetchone()
            if not result:
                # Add the semester if it does not exist
                await add_entity(Semester(year=section.year, semester=section.semester), "semesters", ("year", "semester"))
        
        # Now add the section
        return await add_entity(section, "sections", ("section_number", "number_of_students", "instructor_id", "course_number", "year", "semester"))
    finally:
        if conn.is_connected():
            conn.close()

@router.post("/add-learning-objective/", status_code=201, summary="Add a new learning objective", response_description="Learning objective added successfully")
async def add_learning_objective(learning_objective: LearningObjective):
    return await add_entity(learning_objective, "learning_objectives", ("code", "title", "description"))

@router.post("/associate-course-section/", status_code=201, summary="Associate a course with a section for a specific semester", response_description="Association created successfully")
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

@router.post("/associate-course-with-degree/", status_code=201, summary="Associate a course with a degree", response_description="Course associated with degree successfully")
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

@router.get("/courses-by-degree/", response_model=List[CourseResponse], status_code=200, summary="Get courses by degree", response_description="List of courses for a specific degree")
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

@router.get("/list-sections/", response_model=List[Section])
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

@router.get("/learning-objectives/", response_model=List[LearningObjective])
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

@router.get("/courses-by-objective/", response_model=List[CourseResponse])
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

@router.get("/sections-by-course/", response_model=List[Section])
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

@router.get("/sections-by-instructor/", response_model=List[Section])
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

@router.get("/instructor-sections/", response_model=List[SectionEvaluation])
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


@router.get("/degrees/", response_model=List[DegreeOption])
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

@router.get("/instructors/", response_model=List[InstructorOption])
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

@router.get("/semesters/", response_model=List[Semester])
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


@router.get("/sections-by-instructor-degree-semester/", response_model=List[SectionEvaluationDetail])
async def get_sections_by_instructor_degree_semester(instructor_id: int, degree_name: str, degree_level: str, semester: str, year: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.section_number, s.course_number, c.name AS course_name, s.number_of_students, s.year, s.semester, s.instructor_id,
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
        return [SectionEvaluationDetail(**section) for section in sections]
    finally:
        if conn.is_connected():
            conn.close()

@router.get("/sections-with-evaluations/", response_model=List[SectionEvaluation])
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

@router.post("/associate-course-objective/", status_code=201, summary="Associate a course with a learning objective", response_description="Association created successfully")
async def associate_course_objective(association: CourseObjectiveAssociation):
    return await add_entity(association, "course_learning_objectives", ("course_number", "objective_code"))

@router.post("/update-evaluation/", response_model=dict)
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

@router.get("/get-evaluation/{section_id}", response_model=EvaluationData)
async def get_evaluation(section_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT section_ID, objective_code, eval_criteria, eval_A_count, eval_B_count, eval_C_count, eval_F_count, improvements
        FROM course_evaluations
        WHERE section_ID = %s;
        """
        cursor.execute(query, (section_id,))
        evaluation = cursor.fetchone()
        if evaluation:
            return evaluation
        else:
            raise HTTPException(status_code=404, detail="Evaluation not found")
    finally:
        conn.close()

