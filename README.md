Group Members: Campbell Jin, Michelle Delves, Milan Rama & Rishabh Nagpal

This project implements a python Linear Program to optimize the cost of delivery to Woolworths supermarkets in the Auckland Regions

In order to run the final Linear Program, run the formulation.py script.
In order to perform simulations for evaluating the routes generated, run the simulationWeekday.py and simulationSaturday.py scripts.

A list of the most important individual files is as follows:  <br />

--- createRegionsMatrix.py - reads in list of stores and splits them by regions in an easier to use format. <br />
--- NetworkAdjacencyMatrix.py - contains classes used to enumerate routes.<br />
--- createRoutes.py - creates a set of possible routes for use in the Linear Program. <br />
--- readRoutes.py - Used to read in the output of createRoutes so they can be used in "formulation.py". <br />
--- formulation.py - Runs the linear model and gives outputs of optimal routes per day of the week. Stores the routes generated in the  folder "usedRoutes"<br />
--- readUsedRoutes.py - Reads in the routes genereated by formulation.py and returns either a list of nodes or arcs for each route. <br />
--- Mapping-checkpoint.ipynb - Creates visualisations of the trucking routes genenerated by "formulation.py". <br />
--- simulationWeekday.py - Simulates demands and travel times to determine the quality of the routes generated on Weekdays. Prints out the data from the simulations and plots a histogram of the simulated costs which can be saved. <br />
--- simulationSaturday.py - Performs the same simulation as "simulationWeekday.py" but for the Saturday routes.