import shapefile
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import numpy as np

usmap = shapefile.Reader("geodata\\USA_adm0.shp")
shapes = usmap.shapes()
borderpts = shapes[0].points
xpts, ypts = zip(*borderpts)
start = int(2.9e4)
end = int(1.2e6)
xpts = xpts[start:end:50]
ypts = ypts[start:end:50]
pts = np.asarray(list(zip(xpts, ypts)))
border = ConvexHull(np.asarray(pts))


# %%
fig, ax = plt.subplots(1)
ax.plot(xpts, ypts, marker='o', linestyle='', markersize=2)
# ax.plot(pts[border.vertices, 0], pts[border.vertices, 1], 'k')
plt.show()
