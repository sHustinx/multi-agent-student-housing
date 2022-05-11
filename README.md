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

### Visualization
