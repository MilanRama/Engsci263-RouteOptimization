'''
Creates a dataframe which saves as a csv which stores each of the 
woolworths stores in their respective regions for easier manipulation
'''

import pandas as pd

def regionSwitch(df, i, region):
    '''
    Function to update by region dataframe based on inputs
    '''
    if (region == "Central"):
        df.iloc[i, 2] = 1
    elif (region == "North"):
        df.iloc[i, 3] = 1
    elif (region == "East"):
        df.iloc[i, 4] = 1
    elif (region == "South"):
        df.iloc[i, 5] = 1
    elif (region == "West"):
        df.iloc[i, 6] = 1
    elif (region == "Northwest"):
        df.iloc[i, 7] = 1
    elif (region == "Distribution"):
        df.iloc[i, 2:] = 1

# reads in dataframe and adds rows for each region
df = pd.read_csv("WoolworthsLocations.csv", usecols=(2,5))
df.insert(2, "C", 0)
df.insert(3, "N", 0)
df.insert(4, "E", 0)
df.insert(5, "S", 0)
df.insert(6, "W", 0)
df.insert(7, "NW", 0)

# splits up regions columns for stores shared across multiple regions
df["Regions"] = df["Regions"].str.split('/')

# loops through each store and changes any region they are in to a 1 in their dataframe row
for i in df.index:
    for region in df["Regions"][i]:
        regionSwitch(df, i, region)

# save to csv
df.to_csv("WoolworthsByRegion.csv", columns=("Store","C","N","E","S","W","NW"), index=False)


