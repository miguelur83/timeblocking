from flask import Flask, request, render_template, redirect, flash
from ortools.sat.python import cp_model
import pandas as pd
from pdf import generate_pdf
from project import schedule_blocks, create_timetable, get_project_statistics
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():# Extract available days
    try:
        available_days = request.form.getlist('available_days')
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        # Extract project details
        projects = []
        project_count = int(request.form.get('project_count', 0))  # Use 0 as default if project_count is not present
        for i in range(project_count):
            project_name = request.form.get(f'projects[{i}][name]')
            blocks = int(request.form.get(f'projects[{i}][blocks_per_week]', 3))  # Default to 3 if not present
            hours_per_block = float(request.form.get(f'projects[{i}][hours_per_block]', 1))  # Default to 1 if not present
            if project_name:  # Ensure project name is not None
                projects.append({'name': project_name, 'hours_per_block': hours_per_block, 'blocks_per_week': blocks})

        # Extract fixed constraints
        fixed_constraints = []
        constraint_count = int(request.form.get('constraint_count', 0))  # Use 0 as default if constraint_count is not present
        for i in range(constraint_count):
            constraint_name = request.form.get(f'constraints[{i}][name]')
            constraint_day = request.form.get(f'constraints[{i}][day]')
            constraint_start = request.form.get(f'constraints[{i}][start_time]')
            constraint_end = request.form.get(f'constraints[{i}][end_time]')
            
            if constraint_name and constraint_day and constraint_start and constraint_end:
                fixed_constraints.append({
                    'name': constraint_name,
                    'day': constraint_day,
                    'start_time': constraint_start,
                    'end_time': constraint_end
                })
        
        # Print extracted data for debugging
        print("Available Days:", available_days)
        print("Start Time:", start_time)
        print("End Time:", end_time)
        print("Projects:")
        print(json.dumps(projects, indent=4, skipkeys=False))
        print("Fixed Constraints:")
        print(json.dumps(fixed_constraints, indent=4, skipkeys=False))

        # Schedule the blocks
        status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)
        print(json.dumps(result, indent=4, skipkeys=False)) # debug
        timetable = create_timetable(available_days, start_time, end_time, result)
        
        # Handle scheduling result and generate PDF
        if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
            print("Optimal or feasible solution found.")
            timetable_pdf_path = 'timetable.pdf'
            generate_pdf(timetable, timetable_pdf_path, start_time, end_time, [project['name'] for project in projects] + [constraint['name'] for constraint in fixed_constraints])

            stats = get_project_statistics(projects, result)

            return render_template('results.html', filename=timetable_pdf_path, stats=stats)
        else:
            error_message = "No feasible solution found with the given constraints."
            return render_template('results.html', error=error_message)

    except Exception as e:
        error_message = str(e)
        return render_template('results.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
