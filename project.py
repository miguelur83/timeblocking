from ortools.sat.python import cp_model
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import json

def get_user_inputs(hardcoded = False):
    if hardcoded:
        # Hardcoded user options for testing
        available_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        start_time = '08:00'
        end_time = '18:00'

        projects = [
            {'name': 'Gym', 'hours_per_block': 1, 'blocks_per_week': 3},
            {'name': 'Job Hunt', 'hours_per_block': 2, 'blocks_per_week': 5},
            {'name': 'Analyst work', 'hours_per_block': 2, 'blocks_per_week': 5},
            {'name': 'Write', 'hours_per_block': 2, 'blocks_per_week': 3},
            {'name': 'Read', 'hours_per_block': 1, 'blocks_per_week': 3},
            {'name': 'AI training', 'hours_per_block': 2, 'blocks_per_week': 2},
        ]

        fixed_constraints = [
            {'name': 'Lunch break', 'day': 'Monday', 'start_time': '13:00', 'end_time': '13:30'},
            {'name': 'Lunch break', 'day': 'Tuesday', 'start_time': '13:00', 'end_time': '13:30'},
            {'name': 'Lunch break', 'day': 'Wednesday', 'start_time': '13:00', 'end_time': '13:30'},
            {'name': 'Lunch break', 'day': 'Thursday', 'start_time': '13:00', 'end_time': '13:30'},
            {'name': 'Lunch break', 'day': 'Friday', 'start_time': '13:00', 'end_time': '13:30'},
            {'name': 'Writing group', 'day': 'Tuesday', 'start_time': '14:00', 'end_time': '17:00'},
            {'name': 'Writing group', 'day': 'Thursday', 'start_time': '09:00', 'end_time': '13:00'},
        ]

        return available_days, start_time, end_time, projects, fixed_constraints
    else:
        # Select available days
        day_options = {'Monday to Friday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                    'Monday to Saturday': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
                    'Sunday to Saturday': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']}
        
        print("Select available days:")
        for i, option in enumerate(day_options.keys(), 1):
            print(f"{i}. {option}")
        
        day_choice = int(input("Enter the number corresponding to your choice: "))
        available_days = day_options[list(day_options.keys())[day_choice - 1]]

        # Enter start and end times
        start_time = input("Enter start time (HH:MM): ")
        end_time = input("Enter end time (HH:MM): ")

        # Enter list of projects
        projects_input = input("Enter the list of comma-separated projects: ")
        project_names = [name.strip() for name in projects_input.split(',')]

        # Enter blocks and hours per block for each project
        projects = []
        for project_name in project_names:
            blocks = int(input(f"Enter the number of desired weekly blocks for {project_name}: "))
            hours_per_block = float(input(f"Enter the hours per block (increments of .5 hours) for {project_name}: "))
            projects.append({'name': project_name, 'hours_per_block': hours_per_block, 'blocks_per_week': blocks})

        # Enter fixed constraints
        fixed_constraints = []
        add_constraint = input("Do you want to add fixed constraints? (y/n): ")
        while add_constraint.lower() == 'y':
            constraint_name = input("Enter the name for the fixed constraint (e.g., Lunch break, Meeting, etc): ")
            day = input("Enter the day for the fixed constraint (e.g., Monday): ")
            constraint_start_time = input("Enter the start time for the fixed constraint (HH:MM): ")
            constraint_end_time = input("Enter the end time for the fixed constraint (HH:MM): ")
            fixed_constraints.append({'name': constraint_name, 'day': day, 'start_time': constraint_start_time, 'end_time': constraint_end_time})
            add_constraint = input("Do you want to add another fixed constraint? (y/n): ")

        return available_days, start_time, end_time, projects, fixed_constraints


# Converts time string to datetime
def to_time(time_str):
    return datetime.strptime(time_str, '%H:%M').time()

# Converts time string to slot index using the pre-defined time_slots
def time_to_slot(time_str, time_slots):
    return time_slots.get_loc(time_str)

# Uses ortools to optimize the allocation of the available time to the project blocks.
def schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints):
    model = cp_model.CpModel()

    allocation = {}
    block_start = {}
    day_assigned = {}

    time_slots = pd.date_range(start=start_time, end=end_time, freq='30min')[:-1].strftime('%H:%M')
    num_days = len(available_days)
    num_slots = len(time_slots)
    # print("Num days:", num_days)
    # print("Num slots:", num_slots)

    # Define decision variables
    for project_idx, project in enumerate(projects):
        block_duration_slots = int(project['hours_per_block'] * 2)
        for block in range(project['blocks_per_week']):
            for day in range(num_days):
                for slot in range(num_slots - block_duration_slots + 1):  # Ensure enough slots for a full block
                    block_start[(project_idx, block, day, slot)] = model.NewBoolVar(f'start_{project_idx}_{block}_{day}_{slot}')
                    for s in range(slot, slot + block_duration_slots):
                        allocation[(project_idx, block, day, s)] = model.NewBoolVar(f'alloc_{project_idx}_{block}_{day}_{s}')
            day_assigned[(project_idx, block)] = model.NewIntVar(0, num_days - 1, f'day_assigned_{project_idx}_{block}')

    # Set the fixed constraints
    for constraint in fixed_constraints:
        constraint_day = available_days.index(constraint['day'])
        constraint_start_slot = time_to_slot(constraint['start_time'], time_slots)
        constraint_end_slot = time_to_slot(constraint['end_time'], time_slots)
        
        for slot in range(constraint_start_slot, constraint_end_slot):
            for project_idx, project in enumerate(projects):
                block_duration_slots = int(project['hours_per_block'] * 2)
                for block in range(project['blocks_per_week']):
                    # Prevent the block from starting during fixed constraints
                    if slot < num_slots - block_duration_slots + 1:
                        model.Add(block_start[(project_idx, block, constraint_day, slot)] == 0)
                    # Prevent any allocation during fixed constraints
                    model.Add(allocation[(project_idx, block, constraint_day, slot)] == 0)
    
    # Each project block should be assigned through consecutive slots on the same day
    for project_idx, project in enumerate(projects):
        block_duration_slots = int(project['hours_per_block'] * 2)
        for block in range(project['blocks_per_week']):
            for day in range(num_days):
                for slot in range(num_slots - block_duration_slots + 1):
                    # Ensure consecutive allocation for the block
                    model.Add(sum(allocation[(project_idx, block, day, s)] for s in range(slot, slot + block_duration_slots)) == block_duration_slots).OnlyEnforceIf(block_start[(project_idx, block, day, slot)])
                    model.Add(day_assigned[(project_idx, block)] == day).OnlyEnforceIf(block_start[(project_idx, block, day, slot)])

    # Each slot should be assigned at most one project
    for day in range(num_days):
        for slot in range(num_slots):
            model.Add(sum(allocation[(project_idx, block, day, slot)]
                          for project_idx, project in enumerate(projects)
                          for block in range(project['blocks_per_week'])
                          if (project_idx, block, day, slot) in allocation) <= 1)
    
    # For a given day, only one full block should be assigned for a given project
    for project_idx, project in enumerate(projects):
        for day in range(num_days):
            # Sum over all blocks and possible start slots to ensure only one block starts per day for each project
            model.Add(sum(block_start[(project_idx, block, day, slot)]
                        for block in range(project['blocks_per_week'])
                        for slot in range(num_slots - int(project['hours_per_block'] * 2) + 1)) <= 1)
    
    # Ensure all blocks specified per project are allocated
    for project_idx, project in enumerate(projects):
        model.Add(sum(allocation[(project_idx, block, day, slot )] 
                      for block in range(project['blocks_per_week']) 
                      for day in range(num_days) 
                      for slot in range(num_slots)) == int(project['blocks_per_week'] * project['hours_per_block'] * 2))
        
    # Define a variable to store total separation days for a project
    separation_variables = []
    for project_idx, project in enumerate(projects):
        blocks_per_week = project['blocks_per_week']
        
        if blocks_per_week > 1:  # Only consider projects with more than one block
            for block in range(blocks_per_week - 1):
                # Create variable for separation between current block and the next block
                separation = model.NewIntVar(0, num_days - 1, f'separation_{project_idx}_{block}')
                # Ensure separation calculation
                model.Add(separation == day_assigned[(project_idx, block + 1)] - day_assigned[(project_idx, block)])
                separation_variables.append(separation)
    
    # Maximize the number of slots used (somehow also enforces consecutive slots)
    slot_usage_objective = sum(block_start[(project_idx, block, day, slot)]
                           for project_idx, project in enumerate(projects)
                           for block in range(project['blocks_per_week'])
                           for day in range(num_days)
                           for slot in range(num_slots - int(project['hours_per_block'] * 2) + 1))

    # Maximize the total separation across all blocks
    separation_objective = sum(separation_variables)

    # Combine both objectives
    model.Maximize(slot_usage_objective + separation_objective)
      
    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    status = solver.Solve(model)

    # Extract the allocation from the solution
    result = {}
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Initialize result dictionary with fixed constraints
        for constraint in fixed_constraints:
            constraint_day = available_days.index(constraint['day'])
            constraint_start_slot = time_to_slot(constraint['start_time'], time_slots)
            constraint_end_slot = time_to_slot(constraint['end_time'], time_slots)
            for slot in range(constraint_start_slot, constraint_end_slot):
                result.setdefault(constraint['day'], {})[slot] = constraint['name']

        # Add project allocations to the result
        for day in range(num_days):
            for slot in range(num_slots):
                for project_idx, project in enumerate(projects):
                    for block in range(project['blocks_per_week']):
                        if (project_idx, block, day, slot) in allocation and solver.Value(allocation[(project_idx, block, day, slot)]):
                            project_name = projects[project_idx]['name']
                            # Only set project name if not already occupied by a fixed constraint
                            if slot not in result.get(available_days[day], {}):
                                result.setdefault(available_days[day], {})[slot] = project_name


    # print(json.dumps(result, indent=4, skipkeys=False))

    return status, result

# Function to create a timetable
def create_timetable(available_days, start_time, end_time, result):
    time_slots = pd.date_range(start=start_time, end=end_time, freq='30min')[:-1].strftime('%H:%M')
    timetable = pd.DataFrame(index=time_slots, columns=available_days)
    
    for day, slots in result.items():
        for slot, project_name in slots.items():
            timetable.at[time_slots[slot], day] = project_name
       
    return timetable

# Function to display timetable with tabulate
def print_timetable(timetable, available_days):
    timetable_filled = timetable.fillna('')
    table = tabulate(timetable_filled.reset_index(), headers=['Time'] + available_days, tablefmt='rounded_grid', showindex=False, stralign="center")
    print("\nWeekly Timetable:")
    print(table)

# Function to print project statistics
def get_project_statistics(projects, result, print_stats=False):
    project_stats = {project['name']: {'assigned_slots': 0, 'total_hours': 0} for project in projects}

    for day, slots in result.items():
        for slot, name in slots.items():
            if name in project_stats:
                project_stats[name]['assigned_slots'] += 1

    for project in projects:
        project_name = project['name']
        project_stats[project_name]['total_hours'] = (project_stats[project_name]['assigned_slots'] / 2)  # Each slot is 30 minutes

    stats = []
    for project in projects:
        project_name = project['name']
        initial_blocks = project['blocks_per_week']
        initial_hours = project['hours_per_block'] * project['blocks_per_week']
        assigned_slots = project_stats[project_name]['assigned_slots']
        assigned_hours = project_stats[project_name]['total_hours']
        completion_percentage = assigned_hours / initial_hours

        stats.append({
            "Project Name": project_name,
            "Assigned": f"{completion_percentage:.0%}",
            "Target Blocks": initial_blocks,
            "Hours per Block": project['hours_per_block'],
            "Total Target Hours": initial_hours,
            "Assigned Slots": assigned_slots,
            "Assigned Blocks": int(assigned_slots / 2 / project['hours_per_block']),
            "Total Assigned Hours": assigned_hours
        })

    if print_stats:
        # Print the table using tabulate
        print("\nAssignment Statistics:")
        print(tabulate(stats, headers="keys", floatfmt=".2f", tablefmt='rounded_grid', showindex=False, stralign="center", numalign="center"))
    
    return stats

# Main function
def main():
    available_days, start_time, end_time, projects, fixed_constraints = get_user_inputs()
    status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)
    # print(json.dumps(result, indent=4, skipkeys=False))

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        if status == cp_model.OPTIMAL: print ("Optimal solution found.") 
        else: print ("Feasible solution found.") 

        timetable = create_timetable(available_days, start_time, end_time, result)
        
        get_project_statistics(projects, result, print_stats=True)
        print_timetable(timetable, available_days)
    else:
        print("Solution not feasible")

if __name__ == "__main__":
    main()
