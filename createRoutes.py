'''
Script to be run to generate lists of all available routes given the network for the 
Woolworths Distribution Problem split into certain regions
'''

import pandas as pd
from NetworkAdjacencyMatrix import *

# import of data files for both the stores based on their individual regions and the travel times between stores
locationsDF = pd.read_csv("WoolworthsByRegion.csv")
travelDF = pd.read_csv("WoolworthsTravelDurations.csv")

# initialise a list to store the travel times between stores exclusively in their own regions
RegionDFs = []

# array to be used to iterate through each of the regions
columns = ["C", "N", "E", "S", "W", "NW"]

# loops through regions, creating matrices of travel times between stores in each region 
# (ie simplifying the original dataframe with all stores from all regions)
for i in range(len(columns)):
    RegionDFs.append(travelDF.drop(travelDF[locationsDF[columns[i]] == 0].index))
    notRegion = travelDF["Store"][travelDF[locationsDF[columns[i]] == 0].index]
    RegionDFs[i].drop(notRegion, axis=1, inplace=True)
    RegionDFs[i].to_csv("regionTravelTimes\\" + columns[i] + ".csv", index=True)   # also stores these matrices as .csv files

# initialise a list to network objects each of the individual regions
RegionNetworks = []

# loops through regions, creating network objects for each of them
for i in range(len(columns)):

    # initial creation of network objects.
    network = NetworkByAdjacencyMatrix(columns[i], len(RegionDFs[i]), RegionDFs[i].Store.tolist())

    # creates the networks adjacency matrix by creating links between each node to at least their nearest k neighbors. Also creates spanning tree of the network
    network.addAdjacencies_and_createSpanningTree(RegionDFs[i].drop("Store", axis=1), RegionDFs[i].columns.get_loc("Distribution Centre Auckland")-1, k = 3)

    # adds region to list
    RegionNetworks.append(network)

    # uses network's spanning tree to find a set of the networks fundamental cycles
    RegionNetworks[i].findFundamentalCycles()

    # using the set of fundamental cycles enumerates all valid routes based on some assumptions
    RegionNetworks[i].enumerateRoutes()

    # saves each of the sets of routes to file
    with open("{}.txt".format("regionRoutes\\" + columns[i]), "w") as outputFile:
        for route in RegionNetworks[i].routes:
            outputFile.write(repr(route))
            outputFile.write("\n\n")


