// app.js
function addDegree() {
    const name = document.getElementById('degreeName').value;
    const level = document.getElementById('degreeLevel').value;

    fetch('http://127.0.0.1:8000/add-degree/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            level: level
        })
    })
    .then(response => response.json())
    .then(data => alert('Degree added successfully'))
    .catch(error => alert('Error adding degree: ' + error));
}

function fetchAvailableOptions() {
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

