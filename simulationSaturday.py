import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np
from readUsedRoutes import readUsedRoutes

'''
This script estimates the cost of satisfying actual pallet demands for every store on Weekdays by generating
demands for each store and simulating the effects of traffic to determine to quality of the proposed trucking routes.

This script will record the total costs, the demands of each route, the number of extra trucks require to
furfill excess demands, the extra costs associated with the extra trucks and the total cost of all the routes
for each simulation and print out averages for the elements listed above as well as creat a histogram of the total
costs across the simulatons

Currently the script will run 1000 simulations which can be changed on line 98.
'''


def GenerateDemands():
    '''
    Generates the random demands for every store and stores them into a list

    Inputs : None

    Outputs :
             StoreList: A list containing random demands for each store used in the route

    Notes : None
    '''   
    StoreList = [] # Initialising an empty array
    csv = pd.read_csv('weekendDemands.csv') # Reads in CSV file with the respective min, max and mode values for each store required `
    
    # For loop to loop through all the possible routes and pick out the min, mode and max value for each store and store them into a list 'StoreList'

    for i in range (0,len(csv)):
        if i == 55:
            StoreList.append(0)
        else:
            StoreList.append(np.random.uniform(low = csv.iloc[i]['min'], high = csv.iloc[i]['max']))# Generates random demands for each store using a uniform distribution
    return StoreList

def trafficTravelTimes(routes, demands, allTravelTimes):
    '''
    given an array of the routes and their demands, returns an array of simulated corresponding route times with a traffic factor.
    '''
    #We start with simulating the travel times
    
    #The travel times given no traffic drawing from the arcs read in and the matrix of travel durations given
    noTrafficTimes = []
    for route in routes:
        routeTime = 0
        for step in route:
            routeTime += allTravelTimes[step[0],step[1]]
        
        noTrafficTimes.append(routeTime)
    
    #Uses the lognormal distribution to simulate a travel time for the route
    trafficTimes = []
    for i in range(len(noTrafficTimes)):
        #converting non-traffic travel times
        trafficTimes.append(noTrafficTimes[i] * np.random.lognormal(0.2,0.17)) #used a lognormal distribution to model the effects of traffic
    #the unloading times depends on the demand of the store on that day
    unloadingTimes = np.array(demands) * 7.5 * 60

    return np.add(trafficTimes, unloadingTimes)

def routeExtraTime(routeStores, route, routeExtraDemand, simDemands, allTravelTimes):
    #Calculates the extra costs due to the total demand of a route exceeeding 26 pallets
    directTravelTimes = []
    for store in routeStores:
        storeDirectTravelTime = allTravelTimes[store, 55] + allTravelTimes[55, store]
        directTravelTimes.append((storeDirectTravelTime, store))
    for store in sorted(directTravelTimes, key=lambda tup: tup[0]):
        if simDemands[store[1]] > routeExtraDemand:
            extraTime = store[0]*np.random.lognormal(0.2,0.17) #using the same distribution used for traffic times earlier
            nodeConnected = []
            for step in route:
                if store[1] in step:
                    extraTime -= allTravelTimes[step[0],step[1]]
                    for s in step:
                        if s != store[1]:
                            nodeConnected.append(s)
            extraTime += allTravelTimes[nodeConnected[0],nodeConnected[1]]
            break
    extraTime += routeExtraDemand * 7.5
    return extraTime

# Creating an empty array accounting for the extra cost involved if demand exceeds 26 pallets
extra_cost = []

# Creating an empty array for the cost of the routes accounting for the effects of traffic and unloading times
simulationCosts = []
sim_route_demands = [] #for recording the demands of the routes
sim_overcapacity = []   #for recording the overcapacity

#The number of simulations to run
simulations = 1000

routes = readUsedRoutes("usedRoutes\\Average Saturday Demand.txt", True)
routeStores = readUsedRoutes("usedRoutes\\Average Saturday Demand.txt",False)
allTravelTimes = np.genfromtxt("WoolworthsTravelDurations.csv", delimiter = ",", skip_header = 1, usecols = range(1,67))


for sim in range (simulations):
    #generating random demands for each store
    Run = GenerateDemands()
    route_demands = []
    for route in routeStores:
        total_demand = 0
        for i in range (len(route)):
            if route[i] != 55:
                total_demand += Run[route[i]] # summing the demands for the stores in the route
        route_demands.append(total_demand)# recording the total demand for the route

    #simulates the route times accounting for traffic and variations in unloading times
    total_times = trafficTravelTimes(routes, route_demands, allTravelTimes)
    
    #calculates the cost of the route given the simulated times
    routeCosts = []
    for time in total_times:
        if time <= 4 * 3600:
            routeCosts.append((time/3600)*225)
        else:
            routeCosts.append(225*4 + ((time-(4*3600))/3600)*275)
    

    overcapacity = 0 # created counter variable
    demandExtraCosts = []
    for i in range (len(route_demands)):
        if route_demands[i]>26: # If demand exceeds 26, the counter which refers to how many extra trucks are needed increases
            overcapacity+= 1    # increases the counter i.e the number of extra trucks required each time the demand is exceeded  
            demandExtraCosts.append(routeExtraTime(routeStores[i], routes[i], route_demands[i]-26, Run, allTravelTimes) * 225/3600)
    extra_cost.append(sum(demandExtraCosts))   # Adds the extra cost array, the number of extra trucks required * fixed cost * hours 

    sim_route_demands.append(route_demands) #records the simulated demands
    sim_overcapacity.append(overcapacity)

    #records the cost of the entire set of routes including extra trucks
    simulationCosts.append(np.sum(routeCosts)+extra_cost[-1])

#printing out results
print("For Saturdays:")
print("The mean extra cost from demand fluctuations: ",np.mean(extra_cost))
print("The average demands for each route across simulations:\n", np.sum(sim_route_demands,axis = 0)/simulations)
print("The average number of extra trucks required across simulations:", np.mean(sim_overcapacity))

#Average cost of routes
print("The average cost of the routes:",np.mean(simulationCosts))

# Percentile interval
extra_cost.sort()
print("The percentile interval for extra cost: [",extra_cost[25], extra_cost[975], "]") 

simulationCosts.sort()
print("The percentile interval for the total cost of routes: [",simulationCosts[25], simulationCosts[975], "]")

#Plotting
save_image = True #gives the option for the histogram to be saved or just shown
plt.style.use('seaborn-whitegrid') # adds grid lines in the background
plt.hist(simulationCosts, histtype='stepfilled', facecolor = '#2ab0ff', edgecolor='#169acf', linewidth=0.5,  alpha=0.5)
plt.title("Histogram of Generated Total Costs on Saturday")
plt.xlabel("Total Costs of Routes ($)")
plt.ylabel("Frequency (out of 1000 simulations)")

if save_image:
    plt.savefig("Cost_Saturday_simulations_final.png")
else:
    plt.show()
