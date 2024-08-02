# TIMETABLE GENERATOR
#### Video Demo:  [Youtube link](https://youtu.be/HLyhFN-lRLQ)
## Description:
This application uses Google's OR-Tools to optimize the allocation of timeblocks for specified projects to the available time, resulting in a timetable. It was inspired by my need to allocate my weekly time to several different initiatives. The order in which they appeared each day didn't really matter, and in fact them being "randomized" made each day more interesting (to me) than following the same established routine each day. After some research, I found the OR-Tools tutorial referenced below, and thought it would be a nice chance to learn how to use this tool for general scheduling problems. It was harder than I anticipated.

#### How it works:
The app takes as input the days of the week that are available for scheduling, and the start and end time that will be allocated each day.
Then, it takes the project names to be allocated, the amount of timeblocks for each, and the duration (in 30 min increments) of the timeblocks.
It also allows for "fixed constraints" to be entered, allowing the user to select certain times that will not be open for allocation, and rather assigned to specified tasks or projects (for instance, lunch breaks.)

The application will then attempt to allocate the available time to the projects' timeblocks, following several constraints:
1. Only 1 timeblock for each project can be assigned per day.
2. The timeblocks should be as separated as possible from each other (spread out during the week) for a single project.
3. Obviously, only one project can be assigned to any given slot in the timetable.
4. It will attempt to maximize the use of time and to assign all timeblocks needed for each project.

#### How does it solve the problem:
For this, it uses OR-Tools, a free and open-source software suite developed by Google, specifically the CP-SAT solver within, to solve a scheduling problem with Constraint programming (CP), as shown [here](https://developers.google.com/optimization/scheduling/employee_scheduling). 

The application also uses the following libraries:
1. Pandas, a software library for data manipulation and analysis, specifically used to handle a DataFrame holding the resulting timetable.
2. Datetime to handle dates and times in the timetable.
3. Tabulate to print resulting tables in the terminal.

#### Results:
An optimal solution may be found that satisfies all constraints, or a feasible solution that maximizes the use of time and assignments, or it may not find a feasible solution.

The application will then print some statistics on the assignments for each project, and the resulting timetable.

## User interface:
I wanted to be able to showcase this project on my LinkedIn page and my github page, as a working web application, which required several other pieces to be implemented:
1. I created an index.html page with a form for the user to input the initial variables, using bootstrap to achieve a simple interface.
2. I created a pdf.py script that takes the resulting timetable from the main script and creates a pdf file that the user can view on their browser or download.
3. I created a results.html page to show the script's results and assignment statistics, along with the links to the resulting PDF timetable.
4. I integrated this web application using flask, a micro web framework in python, following several tutorials found on the internet.

(It should be mentioned that I was a web developer and a software engineer before taking on this course to learn python.)

All things considered, I'm very happy with the results, and have other ideas to implement small python applications. My next goal is the CS50 Intro to AI.