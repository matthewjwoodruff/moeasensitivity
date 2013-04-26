"""
Control maps.
I want all algorithms together, for each obj_eps
combinaition.  PopSize on abscissa, NFE on ordinate.
"""
import os
import argparse
import numpy
import pandas
import matplotlib
from matplotlib.backends import backend_svg as svg
from matplotlib.backends import backend_agg as agg

def tickify(rangex, rangey, ax, nticks=5):
    xmin, xmax = ax.get_xlim()
    xmin = round(xmin, 0)
    xmax = round(xmax, 0)
    xstep = (xmax - xmin) / (nticks - 1)
    ax.set_xticks(numpy.arange(xmin, xmax + xstep, xstep))
    ymin, ymax = ax.get_ylim()
    ymin = round(ymin, 0)
    ymax = round(ymax, 0)
    ystep = (ymax - ymin) / (nticks - 1)
    ax.set_yticks(numpy.arange(ymin, ymax + ystep, ystep))

    xvalmin, xvalmax, xvalstep = rangex
    roundingfactor = xvalmax / 10
    xticklabels = ["{0:.0f}".format(max(xvalmin,
                      roundingfactor * round(val/roundingfactor, 0))
                      )
                   for val in 
                   numpy.arange(xvalmin, xvalmax+xvalstep, xvalstep)]
    ax.set_xticklabels(xticklabels)

    yvalmin, yvalmax, yvalstep = rangey
    roundingfactor = yvalmax / 10
    yticklabels = ["{0:.0f}".format(max(yvalmin,
                      roundingfactor * round(val/roundingfactor, 0))
                      )
                   for val in 
                   numpy.arange(yvalmin, yvalmax+yvalstep, yvalstep)]
    ax.set_yticklabels(yticklabels)
    
def controlmaps(fig, algos, problems, paramsdir, **kwargs):
    stat = kwargs.get("stat", "mean")
    metric = kwargs.get("metric", "Hypervolume")
    dirname = kwargs.get("dirname", 
                         "/gpfs/scratch/mjw5407/task1/stats")
    best = 0.0
    worst = 1.0
    meshes = []
    ranges = []
    nticks = 3
    for algo in algos:
        params = pandas.read_table(os.path.join(paramsdir, 
                                   "{0}_Params".format(algo)), 
                                   sep=" ", header=None,
                                   names = ["param", "low", "high"])
        params.set_index("param", inplace=True)
        rows = "maxEvaluations"
        if "Borg" in algo:
            cols = "initialPopulationSize"
        else:
            cols = "populationSize"
        xvalmin = params.ix[cols].min()
        xvalmax = params.ix[cols].max()
        xvalstep = (xvalmax - xvalmin) / (nticks - 1)
        yvalmin = params.ix[rows].min()
        yvalmax = params.ix[rows].max()
        yvalstep = (yvalmax - yvalmin) / (nticks - 1)
        ranges.append( ( (xvalmin, xvalmax, xvalstep),
                         (yvalmin, yvalmax, yvalstep) )  )
        meshrow = []
        meshes.append(meshrow)
        for problem in problems:
            fn = os.path.join(dirname, "{0}_{1}_{2}_{3}_{4}".format(
                              cols, rows, stat, algo, problem))
            table = pandas.read_table(fn, sep=" ")
            mesh = pandas.pivot_table(table, values = metric,
                                      rows = "grid_{0}".format(rows),
                                      cols = "grid_{0}".format(cols))
            meshrow.append(mesh)
            best = max(best, table[metric].max())
            worst = min(worst, table[metric].min())

    best = kwargs.get("best", best)
    worst = kwargs.get("worst", worst)
    nrows = len(algos)
    ncols = len(problems)
    jet_r = matplotlib.cm.get_cmap("jet_r")
    norm = matplotlib.colors.Normalize(vmax=best, vmin=worst)

    for ii in range(nrows):
        rangex, rangey = ranges[ii]
        for jj in range(ncols):
            ax = fig.add_subplot(nrows, ncols, ncols * ii + jj + 1)
            ax.contourf(meshes[ii][jj], 100, cmap=jet_r, norm=norm)
            tickify(rangex, rangey, ax, nticks)
            

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("algos", 
                        help="comma-separated list of algorithms")
    parser.add_argument("problems",
                        help="comma-separated list of problems")
    parser.add_argument("-s", "--stat", default="mean",
                        help="statistic for control maps")
    parser.add_argument("-m", "--metric", default="Hypervolume",
                        help="metric for control maps")
    parser.add_argument("-d", "--stats-directory",
                        default="/gpfs/scratch/mjw5407/task1/stats",
                        help="directory with statistics files")
    parser.add_argument("-o", "--output-file",
                        default="./controlmaps.png")
    parser.add_argument("-b", "--best", type=float,
                        help = "override best metric value")
    parser.add_argument("-w", "--worst", type=float,
                        help = "override worst metric value")
    parser.add_argument("-p", "--params-dir", default="./params")
    return parser.parse_args()

def cli():
    args = get_args()
    algos = args.algos.split(",")
    print algos
    problems = args.problems.split(",")
    print problems
    nalgos = len(algos)
    nproblems = len(problems)

    fig = matplotlib.figure.Figure(figsize=(nproblems*2, nalgos*2))
    fig.subplots_adjust(left=0.07, right=0.95, top=0.97, bottom=0.02, 
                        wspace = 0.25, hspace=0.25)
    agg.FigureCanvasAgg(fig)
    keywords = {}
    keywords["stat"] = args.stat
    keywords["metric"] = args.metric
    keywords["dirname"] = args.stats_directory
    if args.best is not None:
        keywords["best"] = args.best
    if args.worst is not None:
        keywords["worst"] = args.worst

    controlmaps(fig, algos, problems, args.params_dir, **keywords)

    fig.savefig(args.output_file)
    
if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
