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
controlmaps.py

Control maps.
all algorithms together, for each obj_eps
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
    xstep = (xmax - xmin) / (nticks )
    ax.set_xticks(numpy.arange(xmin+xstep, xmax , xstep))
    ymin, ymax = ax.get_ylim()
    ymin = round(ymin, 0)
    ymax = round(ymax, 0)
    ystep = (ymax - ymin) / (nticks )
    ax.set_yticks(numpy.arange(ymin, ymax +ystep, ystep))

    xvalmin, xvalmax, xvalstep = rangex
    roundingfactor = xvalmax / 10
    xticklabels = ["{0:.0f}".format(
                      roundingfactor * round(val/roundingfactor, 0)
                      )
                   for val in 
                   numpy.arange(xvalmin+xvalstep, xvalmax, xvalstep)]
    ax.set_xticklabels(xticklabels)

    yvalmin, yvalmax, yvalstep = rangey
    roundingfactor = yvalmax / 10
    yticklabels = ["{0:.0f}".format(max(yvalmin,
                      roundingfactor * round(val/roundingfactor, 0))
                      )
                   for val in 
                   numpy.arange(yvalmin, yvalmax+yvalstep, yvalstep)]
    ax.set_yticklabels(yticklabels)

def colorbar(fig, cmap, worst, best, **kwargs):
    sm = matplotlib.cm.ScalarMappable(cmap=cmap) 
    sm.set_array([worst, best])
    cbar = fig.colorbar(sm)
    cbax = cbar.ax
    box = cbax.get_position()
    box = box.shrunk(0.4,1.0)
    cbax.set_position(box, which="both")
    cbax.set_frame_on(True)
    cbax.set_aspect("auto")

    context_l = kwargs.get("context_l", worst)
    context_h = kwargs.get("context_h", best)
    slope = 1.0 / (best - worst)
    intercept = - worst * slope
    lo = slope * context_l + intercept
    hi = slope * context_h + intercept
    cbax.set_ylim((lo, hi))
    cbax.set_ybound((lo,hi))
    cbar.set_ticks([
        0.001 * numpy.ceil(1000*cbar.vmin),
        0.001 * numpy.floor(1000*cbar.vmax)])



    
def controlmaps(fig, algos, problems, paramsdir, **kwargs):
    stat = kwargs.get("stat", "mean")
    metric = kwargs.get("metric", "Hypervolume")
    dirname = kwargs.get("dirname", 
                         "/gpfs/scratch/mjw5407/task1/stats")
    best = 0.0
    worst = 1.0
    meshes = []
    ranges = []
    nticks = 5
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
        xvalstep = (xvalmax - xvalmin) / (nticks )
        yvalmin = params.ix[rows].min()
        yvalmax = params.ix[rows].max()
        yvalstep = (yvalmax - yvalmin) / (nticks )
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
    print worst, best
    nalgos = len(algos)
    nprobs = len(problems)
    if not kwargs.get("invert", False):
       cmap = matplotlib.cm.get_cmap("jet_r")
    else:
        cmap = matplotlib.cm.get_cmap("jet")

    norm = matplotlib.colors.Normalize(vmax=best, vmin=worst)

    for jj in range(nprobs):
        rangex, rangey = ranges[jj]
        for ii in range(nalgos):
            ax = fig.add_subplot(nprobs, nalgos, 
                                 nalgos * jj + ii + 1)
            contour = ax.contourf(meshes[ii][jj], 100, 
                                  cmap=cmap, norm=norm,
                                  rasterized=True)
            #contour.set_rasterized(True)
            tickify(rangex, rangey, ax, nticks)
            ax.set_xlabel("population size")
            if ii == 0:
                ax.set_ylabel("maximum evaluations")
            ax.set_title(algos[ii])
            ax.label_outer() 

    colorbar(fig, cmap, worst, best, **kwargs)

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
                        default="./controlmaps")
    parser.add_argument("-b", "--best", type=float,
                        help = "override best metric value")
    parser.add_argument("-w", "--worst", type=float,
                        help = "override worst metric value")
    parser.add_argument("-p", "--params-dir", default="./params")
    parser.add_argument("-L", "--cbar-context-low", type=float,
                        help="color bar context low limit.  "\
                             "-b and -w override the actual color "\
                             "normalization."\
                             "Color bar "\
                             "context squishes the color bar to "\
                             "show where it lies in the context "\
                             "of other sets of control maps.")
    parser.add_argument("-H", "--cbar-context-high", type=float,
                        help="color bar context high limit.  "\
                             "-b and -w override the actual color "\
                             "normalization."\
                             "Color bar "\
                             "context squishes the color bar to "\
                             "show where it lies in the context "\
                             "of other sets of control maps.")

    parser.add_argument("-S", "--svg", action = "store_true",
                        help = "produce svg output. "\
                               "default is png")

    return parser.parse_args()

def cli():
    args = get_args()
    algos = args.algos.split(",")
    print algos
    problems = args.problems.split(",")
    print problems
    nalgos = len(algos)
    nproblems = len(problems)

    fig = matplotlib.figure.Figure(figsize=(nalgos*3, nproblems*2.2))
    if args.svg:
        svg.FigureCanvasSVG(fig)
    else:
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
    fig.subplots_adjust(right=0.88, wspace = 0.03, hspace=0.3)

    fig.savefig(args.output_file)
    
if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
