import numpy as np


def readRoutes(fname, size):
    '''
    Reads the adjacency matrices in the files in the regionRoutes folder

    Inputs: fname: String containing the name of the file to be read
            size: integer containing the size of the matrices. This is equal to 
            the number of nodes in the region

    Output: routes: np.array list containing matrices in order.
    '''

    routes = []
    with open(fname, 'r') as f:
        lines = f.readlines()

    route = np.zeros((size, size))
    i = 0
    for line in lines:
        line = line[2:-2]
        if line == (""):
            routes.append(route)
            route = np.zeros((size, size))
            i = 0
        elif line[1] == ' ':
            if line[-1] == ']':
                line = line[:-1]
            route[i, :] = np.fromstring(line, sep = " ")
            i+=1
        elif line[2] == ' ':
            line = line[1:]
            route[i, :] = np.fromstring(line, sep = " ")
            i+=1

    return routes

if __name__ == '__main__':
    routes = readRoutes("regionRoutes\C.txt", 13)
    