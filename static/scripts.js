document.getElementById('start_time').addEventListener('change', function () {
    var startTime = document.getElementById('start_time').value;
    document.querySelectorAll('input[id^="constraint_start"]').forEach(function (input) {
        input.min = startTime;
    });
    document.querySelectorAll('input[id^="constraint_end"]').forEach(function (input) {
        input.min = startTime;
    });
});

document.getElementById('end_time').addEventListener('change', function () {
    var endTime = document.getElementById('end_time').value;
    document.querySelectorAll('input[id^="constraint_start"]').forEach(function (input) {
        input.max = endTime;
    });
    document.querySelectorAll('input[id^="constraint_end"]').forEach(function (input) {
        input.max = endTime;
    });
});

function addProject() {
    var projectCount = parseInt(document.getElementById('project_count').value);
    var projectsContainer = document.getElementById('projects-container');
    var newRow = document.createElement('tr');

    newRow.innerHTML = `
        <td><input type="text" class="form-control" name="projects[${projectCount}][name]" required></td>
        <td><input type="number" class="form-control" name="projects[${projectCount}][blocks_per_week]" value="3" min="1" required></td>
        <td><input type="number" class="form-control" name="projects[${projectCount}][hours_per_block]" value="1" step="0.5" min="0.5" max="24" required></td>
        <td><button type="button" class="btn btn-danger remove-btn" onclick="removeProject(this)">Remove</button></td>
    `;

    projectsContainer.appendChild(newRow);
    document.getElementById('project_count').value = projectCount + 1;
}

function removeProject(button) {
    var row = button.parentElement.parentElement;
    row.parentElement.removeChild(row);
}

function addConstraint() {
    var constraintCount = parseInt(document.getElementById('constraint_count').value);
    var constraintsContainer = document.getElementById('constraints-container');
    var newRow = document.createElement('tr');

    newRow.innerHTML = `
        <td>
            <select class="form-control" name="constraints[${constraintCount}][day]" required>
                <option value="Sunday">Sunday</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
            </select>
        </td>
        <td><input type="time" class="form-control" id="constraint_start_${constraintCount}" name="constraints[${constraintCount}][start_time]" required></td>
        <td><input type="time" class="form-control" id="constraint_end_${constraintCount}" name="constraints[${constraintCount}][end_time]" required></td>
        <td><input type="text" class="form-control" name="constraints[${constraintCount}][name]" required></td>
        <td><button type="button" class="btn btn-danger remove-btn" onclick="removeConstraint(this)">Remove</button></td>
    `;

    constraintsContainer.appendChild(newRow);
    document.getElementById('constraint_count').value = constraintCount + 1;
}

function removeConstraint(button) {
    var row = button.parentElement.parentElement;
    row.parentElement.removeChild(row);
}

function validateConstraints() {
    var availableDays = Array.from(document.querySelectorAll('input[name="available_days"]:checked')).map(cb => cb.value);
    var startTime = document.getElementById('start_time').value;
    var endTime = document.getElementById('end_time').value;

    var constraints = document.querySelectorAll('#constraints-container tr');
    for (var i = 0; i < constraints.length; i++) {
        var day = constraints[i].querySelector('select').value;
        var constraintStart = constraints[i].querySelector('input[name*="[start_time]"]').value;
        var constraintEnd = constraints[i].querySelector('input[name*="[end_time]"]').value;

        if (!availableDays.includes(day)) {
            alert(`Constraint on ${day} is not allowed. Please choose an available day.`);
            return false;
        }

        if (constraintStart < startTime || constraintEnd > endTime) {
            alert(`Constraint from ${constraintStart} to ${constraintEnd} is out of the available time range (${startTime} to ${endTime}).`);
            return false;
        }
    }
    return true;
}