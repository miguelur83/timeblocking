from project import schedule_blocks, create_timetable, get_project_statistics, print_timetable
from ortools.sat.python import cp_model
import pytest
import pandas as pd
from io import StringIO
import sys

def test_schedule_blocks():
    # Get a valid set of user inputs:
    available_days, start_time, end_time, projects, fixed_constraints = valid_user_inputs()
    status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)

    # Verify the model is resolved and an optimal solution is found by ortools:
    assert status == cp_model.OPTIMAL

    stats = get_project_statistics(projects, result)
    #Verify there are assignment statistics:
    assert len(stats) > 0

    #Verify that all projects were assigned at 100%:
    for project in stats:
        assert project["Assigned"] == "100%"

    # Set the available time so constraints are outside of the available time:
    end_time = "15:00"

    # Verify that schedule_blocs throws a KeyError:
    with pytest.raises(KeyError):
        status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)

    # Set an impossible scheduling problem:
    available_days, start_time, end_time, projects, fixed_constraints = invalid_user_inputs()

    # Check the problem can't be solved:
    status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)
    assert status == cp_model.INFEASIBLE


def test_create_timetable():
    # Get a valid set of user inputs:
    available_days, start_time, end_time, projects, fixed_constraints = valid_user_inputs()
    status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)

    # Verify create_timetable returns a DataFrame
    timetable = create_timetable(available_days, start_time, end_time, result)
    assert isinstance(timetable, pd.DataFrame)


def test_print_timetable():
    # Get a valid set of user inputs:
    available_days, start_time, end_time, projects, fixed_constraints = valid_user_inputs()
    status, result = schedule_blocks(available_days, start_time, end_time, projects, fixed_constraints)
    timetable = create_timetable(available_days, start_time, end_time, result)

    # I googled how to assert print statements
    capturedOutput = StringIO()         # Make StringIO.
    sys.stdout = capturedOutput                  # Redirect stdout.
    print_timetable(timetable, available_days)
    sys.stdout = sys.__stdout__                  # Reset redirect.
    assert capturedOutput.getvalue().find("Weekly Timetable:")

def valid_user_inputs():
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

def invalid_user_inputs():
    # Hardcoded user options for testing
    available_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    start_time = '08:00'
    end_time = '18:00'

    projects = [
        #TOO MANY TIMEBLOCKS TO SCHEDULE!
        {'name': 'Gym', 'hours_per_block': 1, 'blocks_per_week': 3},
        {'name': 'Job Hunt', 'hours_per_block': 2, 'blocks_per_week': 5},
        {'name': 'Analyst work', 'hours_per_block': 2, 'blocks_per_week': 5},
        {'name': 'Write', 'hours_per_block': 2, 'blocks_per_week': 5},
        {'name': 'Read', 'hours_per_block': 1, 'blocks_per_week': 5},
        {'name': 'AI training', 'hours_per_block': 2, 'blocks_per_week': 4}, 
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