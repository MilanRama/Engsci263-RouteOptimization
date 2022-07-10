import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("WoolworthsLocations.csv", usecols=(2,3,4))

BBox = (df.Long.min(), df.Long.max(), df.Lat.min(), df.Lat.max())

map = plt.imread("aucklandMap.png")

fig, ax = plt.subplots()
ax.scatter(df.Long, df.Lat, zorder=1, alpha= 1, c='b', s=10)

for index, row in df.iterrows():
    plt.text(x=row['Long'], y=row['Lat'], s=row['Store'], alpha = 0.7, fontsize = 5)
ax.set_title('Plotting Spatial Data on Map')
ax.set_xlim(BBox[0],BBox[1])
ax.set_ylim(BBox[2],BBox[3])
ax.imshow(map, zorder=0, extent = BBox, aspect= 'equal')
plt.savefig("WoolworthsLocationsMap")
plt.show()