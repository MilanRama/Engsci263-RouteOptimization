'''
Defines certain classes used to store networks and enumerate some of the routes within those networks
'''

from os import path
import numpy as np
from numpy.core.numeric import count_nonzero
import pandas as pd
from pulp.apis.core import initialize
from createBitStrings import *

class AdjacencyMatrix(object):
    '''
    Generic superclass to represent graphs as adjacency matrices
    '''
    def __init__(self, name, numNodes, nodeNames):
        self.name = name
        self.matrix = np.zeros((numNodes, numNodes))
        self.nodeNames = nodeNames

    def __repr__(self):
        return "{}: \n {}".format(self.name, self.matrix)

    def __str__(self):
        return "{}: \n {}".format(self.name, self.matrix)

class NetworkByAdjacencyMatrix(AdjacencyMatrix):
    '''
    Class to represent a network as an adjacency matrix. Stores a spanning tree of itself and has methods to generate its own adjacencies, fundamental cycles and routes given certain restrictions.
    '''
    def __init__(self, name, numNodes, nodeNames):
        super().__init__(name, numNodes, nodeNames)
        self.fundamentalCycles = []
        self.routes = []

    def addAdjacencies_and_createSpanningTree(self, travelDF, distributionIndex, k):
        '''
        method to create the networks adjacencies by linking nodes to at least their nearest k neighbors, while the distribution center has connections to all nodes

        Inputs:
            travelDF - pandas dataframe of travel times between nodes in the network
            distributionIndex - index of the distribution center in the dataframe
            k - minimum number of connection for a node to have
        '''
        arr = travelDF.to_numpy()

        # loops through nodes
        for i in range(len(self.matrix)):

            # checks if node is the distribution center. If so adds connections to all other nodes
            if i == distributionIndex:
                self.matrix[i, :] = 1
                self.matrix[:, i] = 1
                self.matrix[i, i] = 0
            
            # if not the distribution center, adds connections to the nearest k other nodes
            else:
                smallest_k_indices = np.argpartition(arr[i, :], k)
                self.matrix[i, smallest_k_indices[:k]] = 1
                self.matrix[smallest_k_indices[:k], i] = 1
                self.matrix[i, i] = 0

        self.spanningTree = NetworkSpanningTree(self)

    def findTreePath(self, finalNode):
        '''
        Finds the path to a certain node along the spanning tree using Breadth-First Search (Faster because tree was created using Depth-First Search)
        For use in the findFundamentalCycles method

        Inputs:
            finalNode - index of node being searched
        Outputs:
            pathMatrix - adjacency matrix of path from node 0 to finalNode along the spanning tree
        '''

        # Initializing return
        pathMatrix = np.zeros((len(self.matrix), len(self.matrix)))

        # Checks if start node is node being searched for. If true, immediately returns
        if finalNode == 0:
            return pathMatrix

        # Implementation of BFS to find the path
        stack = [0]
        parents = [None] * len(self.matrix)
        visited = [False] * len(self.matrix)
        visited[0] = True
        while stack:
            currentNode = stack[0]
            stack.pop(0)
            for i in range(len(self.matrix)):
                if self.spanningTree.matrix[currentNode, i] == 1 and not visited[i]:
                    stack.append(i)
                    parents[i] = currentNode
                    visited[i] = True

                    # If node being searched for is found, goes back from parent to parent, plotting the path then returning that matrix
                    if i == finalNode:
                        while parents[i] != None:
                            pathMatrix[i,parents[i]] = 1
                            pathMatrix[parents[i], i] = 1
                            i = parents[i]
                        return pathMatrix

    def findFundamentalCycles(self):
        '''
        Finds fundamental cycles in the network by adding each of the routes unused by the spanning tree 1 by 1, and finding any cycles this may make (the fundamental cycles)
        '''

        # Initializing return
        fundCycles = []

        # Finds set of arcs not in the spanning tree
        nonTreeArcs = self.matrix - self.spanningTree.matrix

        # loops through each pair of nodes using nested loops
        for i in range(len(nonTreeArcs)):
            for j in range(i, len(nonTreeArcs)):

                # If an arc not in the spanning tree is found between the pair of nodes, finds the paths along the tree to each of those nodes, adds the arc not in the spanning tree,
                # then performs an XOR operation between the 2 paths to output the fundamental cycle
                if nonTreeArcs[i, j] == 1:
                    pathi = self.findTreePath(i)
                    pathi[i,j] = 1
                    pathi[j,i] = 1
                    pathj = self.findTreePath(j)
                    cycleMatrix = 1*np.logical_xor(pathi, pathj)
                    fundCycles.append(Cycle(self, "Fundamental Cycle" + str(len(fundCycles)), cycleMatrix))

        # Sets objects set of fundamental cycles to the set found
        self.fundamentalCycles = fundCycles

    def enumerateRoutes(self):
        '''
        Finds combinations of valid routes given certain conditions by combining the set of fundamental routes in all possible ways
        '''

        # generate array of combinations
        # first generates all bitstrings length of the fundamentalCycles - 1
        bitstrings = []
        n = len(self.fundamentalCycles) - 1
        arr = [None] * n
        bitstrings = generateBitStrings(bitstrings, n, arr, 0)
        
        # then checks if each fundamental cycle contains the distribution center and if so inserts a 1 at the index of that
        # cycle for each possible combination formed above. This means that the combinations included will always include the 
        # distribution center at least once.
        bitstrings_final = []
        for i in range(len(self.fundamentalCycles)):
            if (self.fundamentalCycles[i].matrix[self.nodeNames.index("Distribution Centre Auckland"), :]).sum() != 0:
                for bitstring in bitstrings[:]:
                    b = bitstring.copy()
                    b.insert(i, 1)
                    bitstrings_final.append(b)

                    # removes certain bitstrings to avoid repeats
                    if i != len(bitstring) and bitstring[i] == 1:
                        bitstrings.remove(bitstring)

        #initialize output list
        routes = []

        # loops through bitstrings, checking if each combination is feasible by checking if each of the cycles has at least 1 arc in common. 
        # if so, it performs XOR operations between each of the used cycles (the 1's in the bitstring)
        for bitstring in bitstrings_final:
            # route initialization
            route = Cycle(self, "route"+str(len(routes)), np.zeros((len(self.nodeNames), len(self.nodeNames))))
            routeStarted = False
            broken = False
            for i in range(len(bitstring)):
                if bitstring[i] == 1:

                    # checks if any fundamental cycles have been added yet.
                    # If yes checks if new cycle to be added has any edges in common.
                    if routeStarted:

                        # If no edges in common, stops route from being finished and won't add it to final routes
                        if route.cycleAND(self.fundamentalCycles[i]).sum() == 0:
                            broken = True
                            break
                        # If one or more edges are shared, merges them using XOR
                        else:
                            route.cycleXOR(self.fundamentalCycles[i])
                    # If its the first fundamental cycle to be added, skips the check for shared edges
                    else:
                        route.cycleXOR(self.fundamentalCycles[i])
                        routeStarted = True
            
            # If its a valid route, adds it to the list
            if not broken:
                routeRowSum = np.sum(route.matrix, axis=1)
                if len(np.where(routeRowSum > 0)[0]) <= 5 and len(np.where(routeRowSum > 2)[0]) == 0 and routeRowSum[self.nodeNames.index("Distribution Centre Auckland")] != 0:
                    routes.append(route)
        
        # gets index of distribution center for use in direct route generation
        distrIndex = self.nodeNames.index("Distribution Centre Auckland")

        # loops through nodes apart from distribution center and creates direct routes to and from them to ensure feasibility
        # these matrices have number 2 stored instead of 1 to represent 2x the distance so in the LP, won't have to handle the differently
        for i in range(len(self.matrix)):
            if (i != distrIndex):
                directRouteMatrix = np.zeros((len(self.nodeNames), len(self.nodeNames)))
                directRouteMatrix[i, distrIndex] = 1
                directRouteMatrix[distrIndex, i] = 1
                route = Cycle(self, "route"+str(len(routes)), np.zeros((len(self.nodeNames), len(self.nodeNames))))
                route.cycleXOR(directRouteMatrix)
                route.matrix *= 2
                routes.append(route)

        self.routes = routes

class NetworkSpanningTree(AdjacencyMatrix):
    '''
    Adjacency matrix representing the spanning tree of a network
    '''
    def __init__(self, Network):
        '''
        Automatically creates the tree in class initialization
        '''
        # saves a copy of the network adjacency matrix for itself
        self.networkAdjacency = Network.matrix.copy()
        super().__init__(Network.name + " Spanning Tree", len(self.networkAdjacency), Network.nodeNames)
        self.createTree()

    def createTree(self):
        '''
        creates the spanning tree using a standard Depth First Search, always starting at node 0
        '''
        visited = [1] * len(self.networkAdjacency)
        stack = [0]
        visited[0] = 0
        while len(stack) > 0:
            v = stack[0]
            if np.sum(np.dot(self.networkAdjacency[v, :], visited)) == 0:
                stack.pop(0)
            else:
                tempRow = self.networkAdjacency[v, :]
                toAdd = True
                while toAdd:
                    if visited[np.where(tempRow == 1)[0][0]] == 0:
                        tempRow[np.where(tempRow == 1)[0][0]] = 0
                    else:
                        v2 = np.where(tempRow == 1)[0][0]
                        self.matrix[v,v2] = 1
                        self.matrix[v2,v] = 1
                        visited[v2] = 0
                        stack.insert(0, v2)
                        toAdd = False


class Cycle(AdjacencyMatrix):
    '''
    Adjacency Matrix representing a regular cycle
    '''
    def __init__(self, Network, nameExt, matrix):
        self.networkAdjacency = Network.matrix.copy()
        super().__init__(Network.name + " " + nameExt, len(Network.matrix), Network.nodeNames)
        self.matrix = matrix.copy()

    def cycleXOR(self, other):
        '''
        merges itself with another cycle using an XOR of their adjacency matrices
        
        Inputs:
            other - another adjacency matrix to merge with (of same size)
        '''
        if isinstance(other, AdjacencyMatrix):
            self.matrix = 1 * np.logical_xor(self.matrix, other.matrix)
        elif isinstance(other, np.ndarray):
            self.matrix = 1 * np.logical_xor(self.matrix, other)


    def cycleAND(self, other):
        '''
        checks if this cycle shares any edges with another adjacency matrix using AND
        
        Inputs:
            other - another adjacency matrix structure to merge with (of same size)
        '''
        return 1 * np.logical_and(self.matrix, other.matrix) 

    