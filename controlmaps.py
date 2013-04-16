"""
Control maps.
I want all algorithms together, for each obj_eps
combinaition.  PopSize on abscissa, NFE on ordinate.
"""
import numpy
import pandas
import matplotlib
from matplotlib.backends import backend_svg as svg

def dumbscript():
    data = pandas.read_table("/gpfs/scratch/mjw5407/task1/stats/initialPopulationSize_maxEvaluations_q10_BorgRecency_27_10_1.0", sep=" ")
    data["xcells"] = pandas.cut(
        data["initialPopulationSize"], 
        bins=numpy.arange(0,1100, 100))
    data["xlabels"] = data.apply(
        lambda row: int(row["xcells"][1:-1].split(",")[1]), 
        axis=1)
    data["ycells"] = pandas.cut(
        data["maxEvaluations"], 
        bins=numpy.arange(0, 1100000, 100000))
    data["ylabels"] = data.apply(
        lambda row: int(row["ycells"][1:-1].split(",")[1]),
        axis=1)
    mesh = pandas.pivot_table(data, values="Hypervolume",
                              rows="ylabels",
                              cols="xlabels")
    fig = matplotlib.figure.Figure()
    svg.FigureCanvasSVG(fig)
    ax = fig.add_subplot(1,1,1)
    ax.contourf(mesh)
    ax.set_xticklabels(mesh.columns.values)
    ax.set_yticklabels(mesh.index.values)
    fig.savefig("dumbplot")


def cli():
    dumbscript()

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
