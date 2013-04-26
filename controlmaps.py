"""
Control maps.
I want all algorithms together, for each obj_eps
combinaition.  PopSize on abscissa, NFE on ordinate.
"""
import os
import numpy
import pandas
import matplotlib
from matplotlib.backends import backend_svg as svg

def controlmaps(fig, algos, problems, **kwargs):
    stat = kwargs.get("stat", "mean")
    metric = kwargs.get("metric", "Hypervolume")
    dirname = kwargs.get("dirname", 
                         "/gpfs/scratch/mjw5407/task1/stats")

    best = 0.0
    meshes = []
    for algo in algos:
        rows = "maxEvaluations"
        if "Borg" in algo:
            cols = "initialPopulationSize"
        else:
            cols = "populationSize"
        meshrow = []
        meshes.append(meshrow)
        for problem in problems:
            fn = os.path.join(dirname, "{0}_{1}_{2}_{3}_{4}".format(
                              rows, cols, stat, algo, problem))
            table = pandas.read_table(fn, sep=" ")
            mesh = pandas.pivot_table(table,
                                      values = metric,
                                      rows = "grid_{0}".format(rows),
                                      cols = "grid_{0}".format(cols))
            meshrow.append(mesh)
            best = max(best, table[metric].max())

    nrows = len(algos)
    ncols = len(problems)
    jet_r = matplotlib.cm.get_cmap("jet_r")
    norm = matplotlib.colors.Normalize(vmax=best, vmin=0)

    for ii in range(nrows):
        for jj in range(ncols):
            ax = fig.add_subplot(nrows, ncols, ncols * ii + jj + 1)
            ax.contourf(meshes[ii][jj], 100, cmap=jet_r, norm=norm)


def cli():
    fig = dumbscript()
    fig.savefig("dumbplot")

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
