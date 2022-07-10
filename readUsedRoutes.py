import numpy as np
import pandas as pd
from readRoutes import readRoutes

def readUsedRoutes(fname, arcs):
    with open(fname, 'r') as f:
        lines = f.readlines()

    routeRegions = []
    routeNums = []
    for line in lines:
        if line[7:9] == "NW":
            routeRegions.append("NW")
            routeNums.append(line[15:])
        else:
            routeRegions.append(line[7])
            routeNums.append(line[14:])
    
    sizes = {'C': 13, 'N': 10, 'E': 12, 'S': 15, 'W': 14, 'NW': 11}
    sizesSeries = pd.Series(data=sizes, index=["C", "N", "E", "S", "W", "NW"])

    outputRoutes = []
    i = 0
    arc = []
    region_i = routeRegions[i]
    while i < len(lines):
        regionCurrent = routeRegions[i]
        routes = readRoutes("regionRoutes\\" + regionCurrent + ".txt", sizesSeries.at[regionCurrent])
        regionNodeIndices = np.genfromtxt("regionTravelTimes\\" + routeRegions[i] + ".csv", dtype = np.int8, delimiter = ",", skip_header = 1, usecols = 0)
        while region_i == regionCurrent:
            for j in range(len(routes[int(routeNums[i])])):
                for k in range(j, len(routes[int(routeNums[i])])):
                    if routes[int(routeNums[i])][j,k] != 0:
                        arc.append((regionNodeIndices[j], regionNodeIndices[k]))
            i+=1
            outputRoutes.append(arc)
            arc = []
            try:
                region_i = routeRegions[i]
            except:
                break
    
    if arcs:
        return outputRoutes
    else:
        nodesUsed = []
        for route in outputRoutes:
            routeNodes = []
            for arc in route:
                for node in arc:
                    if node in routeNodes:
                        pass
                    else:
                        routeNodes.append(node)
            nodesUsed.append(routeNodes)
        return nodesUsed

    
if __name__ == "__main__":
    routes = readUsedRoutes("usedRoutes\\Average Weekday Demand.txt", False)
    for route in routes:
        print(route)


