"""
Copyright (C) 2013 Matthew Woodruff

This script is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This script is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this script. If not, see <http://www.gnu.org/licenses/>.

===========================================================
statusplot.py
"""
import pandas
import matplotlib
import matplotlib.backends.backend_svg as svg
from numpy import array

status = pandas.read_table("status.txt", index_col=0)
grouped = status.groupby(["alg", "dv", "obj", "eps"])
status["progress"] = status.apply(lambda row: float(row["sets"]) / row["needed"], axis = 1)
means = grouped["progress"].mean()
width, height = matplotlib.figure.figaspect(0.2)
print width, height
fig = matplotlib.figure.Figure(figsize = (width, height))
svg.FigureCanvasSVG(fig)
colors = means.apply(lambda progress: [[0.7, 0.7, 0.2],[0.2,0.8,0.2]][int(progress)])
subplots = ["Borg", "eMOEA", "eNSGAII", "NSGAII"]
for ii in range(len(subplots)):
    alg = subplots[ii]
    ax = fig.add_subplot(1,4,ii+1)
    co = array(list(colors.ix[alg].values))
    ax.barh(range(6), means.ix[alg].values, color=co)
    ax.set_yticks([])
    ax.set_yticks([0.4 + x for x in range(6)])
    ax.set_yticklabels(["","","","","",""])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "", "0.5", "", "1"])
    ax.set_title(alg)

labels = means.ix["Borg"].index.values
labels = [" ".join([unicode(val) for val in label]) for label in labels]
fig.axes[0].set_yticklabels(labels)

fig.savefig("status_barchart")
