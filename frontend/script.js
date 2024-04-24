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
    const number = document.getElementById('courseNumber').value;
    const name = document.getElementById('courseName').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/add-course/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_number: number, name })
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
    const number = document.getElementById('sectionNumber').value;
    const students = document.getElementById('numberOfStudents').value;
    const instructorId = document.getElementById('sectionInstructorId').value;
    const courseNumber = document.getElementById('sectionCourseNumber').value;
    const semesterYear = document.getElementById('sectionSemesterYear').value;

    try {
        const response = await fetch('http://127.0.0.1:8000/add-section/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                section_number: number,
                number_of_students: students,
                instructor_id: instructorId,
                course_number: courseNumber,
                semester_year: semesterYear
            })
        });
        const data = await response.json();
        alert('Section added successfully: ' + JSON.stringify(data));
    } catch (error) {
        alert('Error adding section: ' + error);
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

async function fetchAvailableOptions() {
    fetch('http://127.0.0.1:8000/available-options/')
    .then(response => response.json())
    .then(data => {
        const optionsDisplay = document.getElementById('optionsDisplay');
        optionsDisplay.innerHTML = ''; // Clear previous content

        const degrees = document.createElement('div');
        degrees.innerHTML = '<h3>Degrees:</h3>' + data.degrees.map(degree => `${degree.name} (${degree.level})`).join(', ');
        
        const semesters = document.createElement('div');
        semesters.innerHTML = '<h3>Semesters:</h3>' + data.semesters.join(', ');

        const instructors = document.createElement('div');
        instructors.innerHTML = '<h3>Instructors:</h3>' + data.instructors.map(instructor => `${instructor.name} (ID: ${instructor.id})`).join(', ');

        optionsDisplay.appendChild(degrees);
        optionsDisplay.appendChild(semesters);
        optionsDisplay.appendChild(instructors);
    })
    .catch(error => {
        console.error('Error loading options:', error);
        alert('Error loading available options: ' + error);
    });
}
