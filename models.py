from pydantic import BaseModel, Field, constr
from typing import List, Optional

class Degree(BaseModel):
    name: str
    level: str

class Course(BaseModel):
    name: str
    department_code: constr(min_length=2, max_length=4)
    course_code: int  # Valid range (1000 to 9999)
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

class EvaluationData(BaseModel):
    section_ID: int
    objective_code: int
    eval_criteria: str
    eval_A_count: int
    eval_B_count: int
    eval_C_count: int
    eval_F_count: int
    improvements: str

class DegreeOption(BaseModel):
    name: str
    level: str

class SemesterOption(BaseModel):
    semester_year: str

class InstructorOption(BaseModel):
    id: int
    name: str

class CourseResponse(BaseModel):
    course_number: str
    course_name: str
    is_core_course: bool

class SectionDetails(BaseModel):
    section_number: int
    course_number: str
    number_of_students: int
    year: int
    semester: str
    course_name: str
    has_evaluation: bool = Field(default=False)

class SectionEvaluation(BaseModel):
    section_number: int
    course_number: str
    number_of_students: int
    year: int
    semester: str
    instructor_id: Optional[int] = None
    evaluation: Optional[EvaluationData] = None

class AvailableOptions(BaseModel):
    degrees: List[DegreeOption]
    semesters: List[str]
    instructors: List[InstructorOption]

class AssociateCourseWithDegree(BaseModel):
    degree_name: str
    degree_level: str
    course_number: str
    core_course: bool

