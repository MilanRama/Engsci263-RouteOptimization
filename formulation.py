import numpy as np
import pandas as pd
from pulp import *

from readRoutes import readRoutes

def formulation(regions, sizes, day, regionDemands, distrIndex):
    '''
    Creates and solves lp models for the entire auckland region for 1 specific day of the week

    Inputs: regions: array containing strings of the region names
            sizes: array containing integer of the size of each region
            day: array containing strings of the days of the week not including sunday
            regionDemands: array containing the demands for each region
            distrIndex: integer containing the index of the distribution centre.

    Outputs: None
             Prints out the Total cost of routes as well as the names of the routes used. 

    Notes: The order of regions and sizes must be in the same order, ie the elements correspond to each other
    '''
    #reading in the possible routes' adjacency matrices

    # Create an array for the properties of each route for every route
    routePalletsDemand = [] #total pallets demand for all stores in a route
    routeTravelTime=[] #total time taken for each store in a route
    routeCost = [] #total cost of the route
    routeStoresCovered = [] #array for each route where a value of 1 is assigned if the corresponding store is in the route and 0 otherwise

    allroutes = []

    x = 0 #to keep track of the regions

    for region in regions:
        RouteNames = []
        routes = readRoutes("regionRoutes\\" + region + ".txt", sizes[x])

        #reading in the travel times between stores in the region
        regionTravelTimes = np.genfromtxt("regionTravelTimes\\" + region + ".csv", delimiter = ",", skip_header = 1, usecols = range(2,sizes[x]+2))

        regionNodeIndices = np.genfromtxt("regionTravelTimes\\" + region + ".csv", dtype = np.int8, delimiter = ",", skip_header = 1, usecols = 0)

        #filtering out the demands for the particular day
        demands = regionDemands[x][day]

        #list of route names
        RouteNames = [regions[x] + " route" + str(i) for i in range(len(routes))]
        allroutes.extend(RouteNames)

        #travel times for each route = summing up the elements in the product between the adjacency matrices and the regionTravelTimes 
        #(element by element) and then dividing by 2


        for route in routes:
            #This results in an average for the 2 directions of the route which is acceptable as the difference is very small
            travelTime = np.sum(np.multiply(route, regionTravelTimes))/2 
            #unloading times
            totalPalletsDemand = 0
            stores = np.sum(route, axis = 1) #gives 0 for a row only if it is not within the route, 2 otherwise 
            
            stores2 = np.zeros(66)
            for i in range(len(stores)):
                stores2[regionNodeIndices[i]] = stores[i]

            for i in range(sizes[x]):
                if stores[i] != 0: #checking if the particular store is within the route
                    totalPalletsDemand += demands.iloc[i] #returns the pallet demand for that store
            
            totalTime = travelTime+ totalPalletsDemand*7.5*60 #adding the travel time with the unloading time

            #adding to the list of route information
            routeTravelTime.append(totalTime)
            routePalletsDemand.append(totalPalletsDemand)

            #calculating rotue costs based on the time taken
            if totalTime <= 4 * 3600:
                routeCost.append((totalTime/3600)*225)
            else:
                routeCost.append(225*4 + ((totalTime-(4*3600))/3600)*275)

            routeStoresCovered.append(stores2/2) # stores already assigns a value of 2 for each store visited and 0 otherwise
        x += 1 #increment as we are moving on to the next region

        
    #Dataframe creation
    RouteTime = pd.Series(routeTravelTime, index = allroutes)
    RouteDemand = pd.Series(routePalletsDemand, index = allroutes)
    RouteCost = pd.Series(routeCost, index=allroutes)
    RouteStores = pd.Series(routeStoresCovered, index=allroutes)
    

    RouteData = pd.DataFrame({'Cost': RouteCost,
                                    'Demand': RouteDemand,
                                    'Time': RouteTime,
                                    'Stores':RouteStores})
      
    #Forming the mixed-interger Program
    prob = LpProblem("Truck Scheduling and Efficiency for Woolworths NZ", LpMinimize)
    
    #creating problem data variable
    route_vars = LpVariable.dicts("Routes", allroutes, cat=LpBinary)

    #creating objective function
    prob += lpSum([RouteCost[i]*route_vars[i] for i in allroutes]) if lpSum(route_vars) <= 60 else lpSum([RouteCost[i]*route_vars[i] for i in allroutes]) + (lpSum(route_vars) - 60) * 2000

    #adding constraints
    for i in allroutes:
        prob += RouteTime[i]*route_vars[i] <= 6*3600  # 6 hour time limit for routes
        prob += RouteDemand[i]*route_vars[i] <= 25  # 26 pallets limit due to truck capacity, reduced to 25 to minimize final overall cost
    for j in range(66):
        if j != distrIndex:
            prob += lpSum([RouteStores[i][j]*route_vars[i] for i in allroutes]) == 1 # each node is visited once and once only
    

    prob.writeLP("Routes_"+ day +".lp")
    prob.solve(PULP_CBC_CMD(msg=0))

    return prob.variables(), prob.objective




if __name__ == '__main__':
    demands = pd.read_excel('WoolworthsDemands.xlsx')
    woolworthsRegion = np.genfromtxt('WoolworthsByRegion.csv', delimiter = ',', skip_header = 1, usecols=(range(1,7)))

    #list of nodes in Central region
    regionCindex = []
    regionEindex = []
    regionNindex = []
    regionNWindex = []
    regionSindex = []
    regionWindex = []


    #Uses the WoolworthsByRegion file to split the data into the 6 regions (with some overlap)

    #creating a list to store the names of nodes in each region
    for i in range(66):
        if woolworthsRegion[i,0] == 1:
            regionCindex.append(i)
        if woolworthsRegion[i,1] == 1:
            regionNindex.append(i)
        if woolworthsRegion[i,2] == 1:
            regionEindex.append(i)
        if woolworthsRegion[i,3] == 1:
            regionSindex.append(i)
        if woolworthsRegion[i,4] == 1:
            regionWindex.append(i)
        if woolworthsRegion[i,5] == 1:
            regionNWindex.append(i)

    #assigning/filtering the  demand for each region
    demandsC = demands[demands.index.isin(regionCindex)]
    demandsN = demands[demands.index.isin(regionNindex)]
    demandsE = demands[demands.index.isin(regionEindex)]
    demandsS = demands[demands.index.isin(regionSindex)]
    demandsW = demands[demands.index.isin(regionWindex)]
    demandsNW = demands[demands.index.isin(regionNWindex)]

    #Formulating a solution for each day of the week
    outputs = []
    objectiveTotals = []
    Days = ["Average Weekday Demand","Average Saturday Demand"]
    for DAY in Days:
        out, obj = formulation(["C", "N", "E", "S", "W", "NW"], [13, 10, 12, 15, 14, 11], DAY, [demandsC, demandsN, demandsE, demandsS, demandsW, demandsNW], 55)
        outputs.append(out)
        objectiveTotals.append(obj)

    #printing out the results of the LP

    #for viewing variable values
    for i in range(len(outputs)):
        with open("{}.txt".format("usedRoutes\\" + Days[i]), "w") as outputFile:
            print(Days[i] + ":")
            print("Total Cost of Routes = $", value(objectiveTotals[i]))
            print("The routes used are:")
            for v in outputs[i]:
                if v.varValue != 0 and v.name != "__dummy":
                    print(v.name)
                    outputFile.write(v.name + "\n")


    print("Total Cost of Routes = $", value(objectiveTotals[0])*5 + value(objectiveTotals[1]))

