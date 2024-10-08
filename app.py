from io import BytesIO
from flask import Flask, logging, request, render_template, session, send_file, abort
from ortools.sat.python import cp_model
import pandas as pd
from pdf import generate_pdf
from project import schedule_blocks, create_timetable, get_project_statistics
import json
import os
import uuid

app = Flask(__name__)

app.secret_key = os.urandom(24)  # Generates a random 24-byte key

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
            pdf_buffer = generate_pdf(timetable, timetable_pdf_path, start_time, end_time, [project['name'] for project in projects] + [constraint['name'] for constraint in fixed_constraints])
           
           # Create a unique identifier for the PDF
            pdf_id = str(uuid.uuid4())
            # Store the PDF buffer in the session or temporary storage
            session[pdf_id] = pdf_buffer.getvalue()

            stats = get_project_statistics(projects, result)

            return render_template('results.html', filename=timetable_pdf_path, stats=stats, pdf_id=pdf_id)
        else:
            error_message = "No feasible solution found with the given constraints."
            return render_template('results.html', error=error_message)

    except Exception as e:
        error_message = str(e)
        return render_template('results.html', error=error_message)

@app.route('/download_pdf/<pdf_id>')
def download_pdf(pdf_id):
    print(f"Attempting to download PDF with ID: {pdf_id}")
    
    try:
        pdf_data = session.get(pdf_id)
        if pdf_data is None:
            abort(404, description="PDF not found")
        
        pdf_bytes = BytesIO(pdf_data.encode('latin1')) 

        return send_file(
            pdf_bytes,
            as_attachment=request.args.get('mode') == 'download',
            download_name='timetable.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return "Error serving PDF", 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port)