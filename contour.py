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
contour.py
joint performance contours.
"""
import argparse
import pandas
import matplotlib
# svg is not realistic due to the number of points being plotted
from matplotlib.backends import backend_agg as agg
import numpy

def get_args():
    description="Joint performance contour plot, showing 3 vs 10 "\
                "objective performance."
    parser = argparse.ArgumentParser()
    parser.add_argument("moeas",
                        help="Comma-separated list of MOEAs for "\
                             "which to make contour plots."
                       )
    return parser.parse_args()

def countsandrange(algo):
    ten = pandas.read_table(
                            "/gpfs/scratch/mjw5407/task1/"\
                            "hv/{0}_27_10_1.0.hv".format(algo), 
                            sep=" ")
    three = pandas.read_table(
                            "/gpfs/scratch/mjw5407/task1/"\
                            "hv/{0}_27_3_0.1.hv".format(algo), 
                            sep=" ")
    data = pandas.DataFrame({"ten": ten.Hypervolume, 
                             "three": three.Hypervolume})
    data["gthree"] = data.three.apply(
                            lambda val: 0.001 * numpy.floor(1000 * val))
    data["gten"] = data.ten.apply(
                            lambda val: 0.001 * numpy.floor(1000 * val))
    binned = data.groupby(["gthree", "gten"]).count()
    total = binned.ten.sum()
    density = binned.ten.apply(lambda val: float(val) / total)
    print "{0}: max density {1}".format(algo, density.max())
    return density, three.Hypervolume.max(), ten.Hypervolume.max()

def contours(fig, algos):
    bindata = []
    three = 0 # max three objective HV
    ten = 0 # max ten objective HV
    for algo in algos:
        car = countsandrange(algo)
        bindata.append(car[0])
        three = max(car[1], three)
        ten = max(car[2], ten)

    maxdensity = max([data.max() for data in bindata])

    counter = 0
    for algo, data in zip(algos, bindata):
        counter += 1
        ax = fig.add_subplot(1, len(algos), counter)
        gridded = data.unstack("gthree")
        cmap = matplotlib.cm.get_cmap("jet")
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxdensity)
        ax.contourf(gridded.columns.values, gridded.index.values,
                    gridded, 100, cmap=cmap, norm=norm)
        ax.set_ylim((0, ten))
        ax.set_xlim((0, three))
    sm = matplotlib.cm.ScalarMappable(cmap=cmap)
    sm.set_array([0, maxdensity])
    fig.colorbar(sm)
    
def cli():
    args = get_args()
     
if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
