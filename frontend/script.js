async function addDegree() {
    const name = document.getElementById('degreeName').value;
    const level = document.getElementById('degreeLevel').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/add-degree/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, level })
        });
        const data = await response.json();
        alert('Degree added successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error adding degree: ' + error);
    }
}

async function addCourse() {
    const name = document.getElementById('courseName').value;
    const departmentCode = document.getElementById('departmentCode').value;
    const courseCode = parseInt(document.getElementById('courseCode').value, 10);

    if (!(courseCode >= 1000 && courseCode <= 9999)) {
        alert('Course code must be between 1000 and 9999.');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/add-course/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, department_code: departmentCode, course_code: courseCode })
        });
        const data = await response.json();
        alert('Course added successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error adding course: ' + error);
    }
}

async function addInstructor() {
    const id = document.getElementById('instructorId').value;
    const name = document.getElementById('instructorName').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/add-instructor/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instructor_id: id, name })
        });
        const data = await response.json();
        alert('Instructor added successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error adding instructor: ' + error);
    }
}

async function addSection() {
    const number = parseInt(document.getElementById('sectionNumber').value);
    const students = parseInt(document.getElementById('numberOfStudents').value);
    const instructorId = parseInt(document.getElementById('sectionInstructorId').value);
    const courseNumber = document.getElementById('sectionCourseNumber').value;
    const semester = document.getElementById('sectionSemester').value;
    const year = parseInt(document.getElementById('sectionYear').value);

    try {
	const response = await fetch('http://127.0.0.1:8000/add-section/', {
	    method: 'POST',
	    headers: { 'Content-Type': 'application/json' },
	    body: JSON.stringify({
		section_number: number,
		number_of_students: students,
		instructor_id: instructorId,
		course_number: courseNumber,
		semester: semester,
		year: year
	    })
	});
	if (!response.ok) throw new Error('Failed to add section. Status: ' + response.status);
	const data = await response.json();
	alert('Section added successfully: ' + JSON.stringify(data));
    } catch (error) {
	alert('Error adding section: ' + error.message);
    }
}

async function addLearningObjective() {
    const code = document.getElementById('objectiveCode').value;
    const title = document.getElementById('objectiveTitle').value;
    const description = document.getElementById('objectiveDescription').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/add-learning-objective/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, title, description })
        });
        const data = await response.json();
        alert('Learning Objective added successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error adding learning objective: ' + error);
    }
}


async function associateCourseWithDegree() {
    const degree_name = document.getElementById('assocDegreeName').value;
    const degree_level = document.getElementById('assocDegreeLevel').value;
    const course_number = document.getElementById('assocCourseNumber').value;
    const core_course = document.getElementById('assocCoreCourse').checked;

    try {
        const response = await fetch('http://127.0.0.1:8000/associate-course-with-degree/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ degree_name, degree_level, course_number, core_course })
        });
        const data = await response.json();
        alert('Course associated with degree successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error associating course with degree: ' + error);
    }
}

async function getCoursesByDegree() {
    const degree_name = document.getElementById('viewDegreeName').value;
    const degree_level = document.getElementById('viewDegreeLevel').value;

    try {
        const response = await fetch(`http://127.0.0.1:8000/courses-by-degree/?degree_name=${encodeURIComponent(degree_name)}&degree_level=${encodeURIComponent(degree_level)}`, {
            method: 'GET'
        });
	const data = await response.json();
        const coursesList = document.getElementById('coursesList');
        coursesList.innerHTML = '<h3>Courses:</h3>' + data.map(course => `${course.course_name} (Number: ${course.course_number}, Core: ${course.is_core_course ? 'Yes' : 'No'})`).join(', ');
    } catch (error) {
        alert('Error viewing courses: ' + error);
    }
}

async function listSections() {
    const startYear = document.getElementById('startYear').value;
    const startSemester = document.getElementById('startSemester').value;
    const endYear = document.getElementById('endYear').value;
    const endSemester = document.getElementById('endSemester').value;

    try {
        const response = await fetch(`http://127.0.0.1:8000/list-sections/?start_year=${startYear}&start_semester=${startSemester}&end_year=${endYear}&end_semester=${endSemester}`, {
            method: 'GET'
        });
        if (!response.ok) throw new Error('Failed to fetch sections. Status: ' + response.status);
        const sections = await response.json();
        const sectionsDisplay = document.getElementById('sectionsDisplay');
        sectionsDisplay.innerHTML = '<h3>Sections:</h3>' + sections.map(section => 
            `Number: ${section.section_number}, Students: ${section.number_of_students}, Instructor ID: ${section.instructor_id}, Course: ${section.course_number}, Year: ${section.year}, Semester: ${section.semester}`
        ).join('<br>');
    } catch (error) {
        alert('Error fetching sections: ' + error.message);
    }
}

async function listLearningObjectives() {
    try {
        const response = await fetch('http://127.0.0.1:8000/learning-objectives/');
        if (!response.ok) throw new Error('Failed to fetch objectives. Status: ' + response.status);
        const objectives = await response.json();
        const objectivesDisplay = document.getElementById('objectivesDisplay');
        objectivesDisplay.innerHTML = '<h3>Objectives:</h3>' + objectives.map(obj => 
            `Code: ${obj.code}, Title: ${obj.title}, Description: ${obj.description}`
        ).join('<br>');
    } catch (error) {
        alert('Error fetching objectives: ' + error.message);
    }
}

async function associateCourseWithObjective() {
    const course_number = document.getElementById('assocCourseNumber_Learning').value;
    const objective_code = document.getElementById('assocObjectiveCode').value;
    
    console.log('Course Number:', course_number); // Log course number
    console.log('Objective Code:', objective_code); // Log objective code

    try {
        const response = await fetch('http://127.0.0.1:8000/associate-course-objective/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_number, objective_code })
        });
        if (!response.ok) throw new Error('Failed to associate. Status: ' + response.status);
        const data = await response.json();
        alert('Course associated with learning objective successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error associating course with objective: ' + error.message);
    }
}

async function getCoursesByObjective() {
    const objectiveCode = document.getElementById('objectiveCodeQuery').value;
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/courses-by-objective/?objective_codes=${objectiveCode}`, {
            method: 'GET'
        });
        if (!response.ok) throw new Error('Failed to fetch courses. Status: ' + response.status);
        const courses = await response.json();
        const coursesDisplay = document.getElementById('coursesByObjectiveDisplay');
        coursesDisplay.innerHTML = '<h3>Courses:</h3>' + courses.map(course => 
            `Name: ${course.course_name} (Number: ${course.course_number}, Core: ${course.is_core_course ? 'Yes' : 'No'})`
        ).join('<br>');
    } catch (error) {
        alert('Error fetching courses: ' + error.message);
    }
}

async function getSectionsByCourse() {
    const courseNumber = document.getElementById('courseNumberQuery').value;
    const startYear = document.getElementById('startYearQuery').value;
    const startSemester = document.getElementById('startSemesterQuery').value;
    const endYear = document.getElementById('endYearQuery').value;
    const endSemester = document.getElementById('endSemesterQuery').value;

    try {
        const response = await fetch(`http://127.0.0.1:8000/sections-by-course/?course_number=${encodeURIComponent(courseNumber)}&start_year=${startYear}&start_semester=${encodeURIComponent(startSemester)}&end_year=${endYear}&end_semester=${encodeURIComponent(endSemester)}`, {
            method: 'GET'
        });
        if (!response.ok) throw new Error('Failed to fetch sections. Status: ' + response.status);
        const sections = await response.json();
        const displayDiv = document.getElementById('sectionsByCourseDisplay');
        displayDiv.innerHTML = '<h3>Sections:</h3>' + sections.map(section =>
            `Section Number: ${section.section_number}, Students: ${section.number_of_students}, Instructor ID: ${section.instructor_id}, Course: ${section.course_number}, Year: ${section.year}, Semester: ${section.semester}`
        ).join('<br>');
    } catch (error) {
        alert('Error fetching sections: ' + error.message);
    }
}

async function getSectionsByInstructor() {
    const instructorId = document.getElementById('instructorIdQuery').value;
    const startYear = document.getElementById('instructorStartYearQuery').value;
    const startSemester = document.getElementById('instructorStartSemesterQuery').value;
    const endYear = document.getElementById('instructorEndYearQuery').value;
    const endSemester = document.getElementById('instructorEndSemesterQuery').value;

    // Check for empty inputs
    if (!instructorId || !startYear || !startSemester || !endYear || !endSemester) {
        alert('Please fill all the fields.');
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/sections-by-instructor/?instructor_id=${instructorId}&start_year=${startYear}&start_semester=${encodeURIComponent(startSemester)}&end_year=${endYear}&end_semester=${encodeURIComponent(endSemester)}`, {
            method: 'GET'
        });
        if (!response.ok) throw new Error('Failed to fetch sections. Status: ' + response.status);
        const sections = await response.json();
        const displayDiv = document.getElementById('sectionsByInstructorDisplay');
        displayDiv.innerHTML = '<h3>Sections:</h3>' + sections.map(section =>
            `Section Number: ${section.section_number}, Students: ${section.number_of_students}, Course Number: ${section.course_number}, Year: ${section.year}, Semester: ${section.semester}`
        ).join('<br>');
    } catch (error) {
        alert('Error fetching sections: ' + error.message);
    }
}

async function submitEvaluation() {
    const sectionID = parseInt(document.getElementById('sectionID').value, 10);
    const objectiveCode = parseInt(document.getElementById('objectiveCode_EvalQuery').value, 10);
    const evalCriteria = document.getElementById('evalCriteria').value;
    const evalACount = parseInt(document.getElementById('evalACount').value, 10);
    const evalBCount = parseInt(document.getElementById('evalBCount').value, 10);
    const evalCCount = parseInt(document.getElementById('evalCCount').value, 10);
    const evalFCount = parseInt(document.getElementById('evalFCount').value, 10);
    const improvements = document.getElementById('improvements').value;

    const evalData = {
        section_ID: sectionID,
        objective_code: objectiveCode,
        eval_criteria: evalCriteria,
        eval_A_count: evalACount,
        eval_B_count: evalBCount,
        eval_C_count: evalCCount,
        eval_F_count: evalFCount,
        improvements: improvements
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/update-evaluation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(evalData)
        });

        if (!response.ok) {
            const message = `An error has occured: ${response.status}`;
            throw new Error(message);
        }

        const result = await response.json();
        alert('Evaluation Submitted Successfully: ' + JSON.stringify(result));
    } catch (error) {
        console.error('Error during evaluation submission:', error);
        alert('Failed to submit evaluation: ' + error.message);
    }
}

async function fetchSections() {
    const instructorId = document.getElementById('instructorId_Eval').value;
    const degreeName = document.getElementById('degreeName_Eval').value;
    const year = new Date().getFullYear();  // Assuming current year; adjust as necessary
    const semester = document.getElementById('semester_Eval').value;

    try {
        const response = await fetch(`http://127.0.0.1:8000/instructor-sections/?instructor_id=${instructorId}&degree_name=${degreeName}&year=${year}&semester=${semester}`);
        if (!response.ok) throw new Error('Failed to fetch sections');
        const sections = await response.json();
        displaySections(sections);  // Implement this function to show sections in the UI
    } catch (error) {
        console.error('Failed to load sections:', error);
    }
}

window.onload = function() {
    fetchInstructors();
    fetchDegrees();
};

async function fetchInstructors() {
    try {
        const response = await fetch('http://127.0.0.1:8000/instructors/');
        const data = await response.json();
        const select = document.getElementById('instructorSelect');
        data.forEach(instructor => {
            let option = document.createElement('option');
            option.value = instructor.id;
            option.textContent = instructor.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to fetch instructors:', error);
    }
}

async function fetchDegrees() {
    try {
        const response = await fetch('http://127.0.0.1:8000/degrees/');
        const data = await response.json();
        const degreeSelect = document.getElementById('degreeSelect');
        const degreeLevelSelect = document.getElementById('degreeLevelSelect');

        // Clear previous options
        degreeSelect.innerHTML = '';
        degreeLevelSelect.innerHTML = '';

        // To store unique degree levels
        const degreeLevels = new Set();

        data.forEach(degree => {
            // Populate degree names
            let option = document.createElement('option');
            option.value = degree.name;
            option.textContent = degree.name;
            degreeSelect.appendChild(option);

            // Collect degree levels
            degreeLevels.add(degree.level);
        });

        // Populate degree levels
        degreeLevels.forEach(level => {
            let levelOption = document.createElement('option');
            levelOption.value = level;
            levelOption.textContent = level;
            degreeLevelSelect.appendChild(levelOption);
        });
    } catch (error) {
        console.error('Failed to fetch degrees:', error);
    }
}


async function fetchSections() {
    const instructorId = document.getElementById('instructorSelect').value;
    const degreeName = document.getElementById('degreeSelect').value;
    const degreeLevel = document.getElementById('degreeLevelSelect').value;
    const semester = document.getElementById('semesterSelect').value;
    const year = document.getElementById('yearInput').value;

    try {
        const url = `http://127.0.0.1:8000/sections-by-instructor-degree-semester/?instructor_id=${instructorId}&degree_name=${degreeName}&degree_level=${degreeLevel}&semester=${semester}&year=${year}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch sections');
        const sections = await response.json();
        displaySections(sections);
    } catch (error) {
        console.error('Failed to load sections:', error);
    }
}

function displaySections(sections) {
    const container = document.getElementById('sectionsContainer');
    container.innerHTML = sections.map(section => {
        // Check if there's an existing evaluation by checking if any key evaluation data is not null
        const hasEvaluation = section.eval_ID !== null;  // or another significant field that indicates evaluation existence
        return `
            <div>
                Section ${section.section_number}: ${section.course_name || 'Course name missing'} (${section.course_number}) - 
                ${hasEvaluation ? 'Evaluation entered' : 'No evaluation yet'}
                <button onclick="showEvaluationForm(${section.section_number}, ${hasEvaluation})">
                    ${hasEvaluation ? 'Update Evaluation' : 'Add Evaluation'}
                </button>
            </div>
        `;
    }).join('');
}

function showEvaluationForm(sectionNumber, hasEvaluation) {
    const formContainer = document.getElementById('evaluationFormContainer');
    formContainer.style.display = 'block';  // Show the form
    const form = document.getElementById('evaluationForm');
    const objectiveInput = document.getElementById('objectiveCode_EvalQuery');

    // Clear the form first
    form.reset();
    document.getElementById('sectionID').value = sectionNumber;

    if (hasEvaluation) {
        loadEvaluationData(sectionNumber);  // Load data if updating
        objectiveInput.setAttribute('readonly', true);  // Make objective code immutable
    } else {
        // Clear the form for a new evaluation
        objectiveInput.value = '';
        objectiveInput.removeAttribute('readonly');  // Allow editing of objective code
        document.getElementById('evalCriteria').value = '';
        document.getElementById('evalACount').value = '';
        document.getElementById('evalBCount').value = '';
        document.getElementById('evalCCount').value = '';
        document.getElementById('evalFCount').value = '';
        document.getElementById('improvements').value = '';
    }
}


async function loadEvaluationData(sectionNumber) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/get-evaluation/${sectionNumber}`);
        const data = await response.json();
        if (data) {
            // Populate form fields with fetched data
            document.getElementById('objectiveCode_EvalQuery').value = data.objective_code || '';
            document.getElementById('evalCriteria').value = data.eval_criteria || '';
            document.getElementById('evalACount').value = data.eval_A_count || '';
            document.getElementById('evalBCount').value = data.eval_B_count || '';
            document.getElementById('evalCCount').value = data.eval_C_count || '';
            document.getElementById('evalFCount').value = data.eval_F_count || '';
            document.getElementById('improvements').value = data.improvements || '';
        }
    } catch (error) {
        console.error('Error loading evaluation data:', error);
        alert('Error loading evaluation data.');
    }
}


function setupEvaluationForm(sectionNumber, courseNumber, evaluation) {
    const form = document.getElementById('evaluationForm');
    form.sectionID.value = sectionNumber;
    if (evaluation && evaluation.eval_ID) {
        // Populate form fields if evaluation exists
        form.objectiveCode_EvalQuery.value = evaluation.objective_code || '';
        form.evalCriteria.value = evaluation.eval_criteria || '';
        form.evalACount.value = evaluation.eval_A_count || '';
        form.evalBCount.value = evaluation.eval_B_count || '';
        form.evalCCount.value = evaluation.eval_C_count || '';
        form.evalFCount.value = evaluation.eval_F_count || '';
        form.improvements.value = evaluation.improvements || '';
    } else {
        // Clear the form for a new evaluation
        form.objectiveCode_EvalQuery.value = '';
        form.evalCriteria.value = '';
        form.evalACount.value = '';
        form.evalBCount.value = '';
        form.evalCCount.value = '';
        form.evalFCount.value = '';
        form.improvements.value = '';
    }
}


async function submitEvaluation() {
    const sectionID = document.getElementById('sectionID').value;
    const objectiveCode = document.getElementById('objectiveCode_EvalQuery').value;
    const evalCriteria = document.getElementById('evalCriteria').value;
    const evalACount = document.getElementById('evalACount').value;
    const evalBCount = document.getElementById('evalBCount').value;
    const evalCCount = document.getElementById('evalCCount').value;
    const evalFCount = document.getElementById('evalFCount').value;
    const improvements = document.getElementById('improvements').value;

    const evalData = {
        section_ID: sectionID,
        objective_code: objectiveCode,
        eval_criteria: evalCriteria,
        eval_A_count: evalACount,
        eval_B_count: evalBCount,
        eval_C_count: evalCCount,
        eval_F_count: evalFCount,
        improvements: improvements
    };

    try {
        const response = await fetch('http://127.0.0.1:8000/update-evaluation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(evalData)
        });

        if (!response.ok) {
            const message = `An error has occured: ${response.status}`;
            throw new Error(message);
        }

        const result = await response.json();
        alert('Evaluation Submitted Successfully: ' + JSON.stringify(result));
        fetchSections();  // Refresh the section list to update the evaluation status
    } catch (error) {
        console.error('Error during evaluation submission:', error);
        alert('Failed to submit evaluation: ' + error.message);
    }
}

function hideEvaluationForm() {
    const formContainer = document.getElementById('evaluationFormContainer');
    formContainer.style.display = 'none';  // Hide the form
    // Optionally, you might want to reset the form here if that's desired behavior
    document.getElementById('evaluationForm').reset();
}


async function fetchLearningObjectives() {
    try {
        const response = await fetch('http://127.0.0.1:8000/learning-objectives/');
        const objectives = await response.json();
        const select = document.getElementById('objectiveCode_EvalQuery'); // Assuming this is your select element ID
        select.innerHTML = ''; // Clear existing options
        objectives.forEach(objective => {
            let option = document.createElement('option');
            option.value = objective.code;
            option.textContent = `${objective.title} (${objective.code})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load learning objectives:', error);
    }
}

document.addEventListener("DOMContentLoaded", fetchLearningObjectives);



