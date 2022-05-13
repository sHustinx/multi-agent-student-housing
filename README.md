# Multi-Agent System: Student Housing

This project implements an agent-based system to compare different distribution methods in student housing.

## Project Setup

### Python
The project was developed with a Python 3.8 environment

The additional packages spade, requests, numpy and matplotlib have to be installed

The current version uses internal messaging, and does not rely on the additional XMPP/Messaging Services required by SPADE

### Simulation Setup

The simulation setup is determined in the utils/constants.py file. 

The general setup for the simulation 
consists of the three constants in the first setup block. These determine the _number of students_ and _houses_, as well as the _distribution of housing methods_ within the system.

| **Parameter**        | **Description**    
|--------------|-----------|
|NUMBER_STUDENTS| number of student agents|
|NUMBER_HOUSES | number of house agents |
|DISTR_METHODS | distribution of methods [COOP, WAIT_LIST, RAND] (values should add up to 1.0)|

In the second setup block, additional parameters of the simulation and visualization can be adjusted.

| **Parameter**        | **Description**    
|--------------|-----------|
|DEFAULT_APPLICATION_DAYS| number of simulation steps until room listings close|
|EXTRA_COOP_DAYS | number of additional simulation steps for co-optation |
|DEFAULT_RENT_PERIOD | default rental period in simulation steps|
|SIMULATION_DURATION | number of simulations steps calculated|
|SAVE_DATA_EVERY_X | trigger for saving data to file|
|CHECK_COMP_EVERY_X | trigger for student agents to re-evaluate situation and available options|
|WARM_UP_TICKS | simulation steps until recording of data starts|

The settings of the two runs we compare in this project are as follows:

| **Parameter**        | **Value**    |
|--------------|-----------|
|Simulation duration | 520 steps | 
|Students | 3000 |
|Houses | (first run) 400, (second run) 600 | 
|Rooms per house | rand(3,7)|
|Rent period | 104 steps |
|Application open | 2 steps |   
|Additional co-op time | 2 ticks | 

### Simulation Results
The simulation generates two timestamped output-files for each run, one .gif and one .json file. 

The gif shows a simplified overview of the student-agents in the system (top-row) and an overview of the house-agents (block below the students).

For the student-agents, dark green shows a student that is currently searching for a room and a light green shows a resident student.
For the houses, each column represents a house, and each row in that column represents a room in that house. If a room is white, it means that there is a student living there, a yellow color means the room is empty and listed. The houses are sorted by attractiveness, from most attractive (left) to least attractive (right).

The json file provides an output of the student and house-data at each simulation step for further visualization and analysis.
Some of the resulting statistics can be seen below:

#### Means of inter-house compatibility

| **Distribution**        | **400 Houses**    |  **600 Houses**    |
|--------------|-----------|----------|
|Co-Optation | avg: 0.933 std: 0.011 |  avg: 0.910 std: 0.017|
|50-50 | avg: 0.909 std: 0.033 |  avg: 0.909 std: 0.027 |
|Random assignment | avg: 0.891 std: 0.018 |  avg:  0.896 std: 0.020|

#### Average waiting-time per student

| **Distribution**        | **400 Houses**    |  **600 Houses**    |
|--------------|-----------|----------|
|Co-Optation | avg: 78.979 std: 106.855 |  avg: 3.783 std: 1.825|
|50-50 | avg: 60.651 std: 59.480 |  avg: 4.101 std: 1.647 |
|Random assignment | avg: 51.980 std: 38.299 |  avg:  4.759 std: 1.751|

#### Number of students (out of 3000) that do not find a room throughout simulation period

| **Distribution**        | **400 Houses**    |  **600 Houses**    |
|--------------|-----------|----------|
|Co-Optation | 63 |  0|
|50-50 | 2 |  0|
|Random assignment | 0 |  0|


### Visualization

#### Simulation-gifs

_The resulting gifs of the simulation runs (co-optation, 50-50, random assignment) with 400 houses and 3000 students:_

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/400_coop.gif) 
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/400_mixed.gif)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/400_random.gif)


_The resulting gifs of the simulation runs (co-optation, 50-50, random assignment) with 600 houses and 3000 students:_

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/600_coop.gif)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/600_mixed.gif)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/600_random.gif)

#### Average Matching-Score

The average matching-score of all houses per simulation step with 400 houses and 3000 students.

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/avg_score_400.svg)

The average matching-score of all houses per simulation step with 600 houses and 3000 students.

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/avg_score_600.svg)


#### Distribution over time

These figures show the distribution of searching/resident student over the simulation-period per distribution method.

_With 400 houses and 3000 students:_

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time1.png)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time2.png)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time3.png)

_With 600 houses and 3000 students:_

![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time4.png)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time5.png)
![](https://github.com/sHustinx/multi-agent-student-housing/blob/main/visualization/dist-over-time6.png)
