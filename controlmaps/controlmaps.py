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
import matplotlib.colorbar
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

def colorbar(fig, cmap, sausage, beast, **kwargs):
    """
    sausage: worst
    beast: best
    Because you can't have positional arguments with the same
    name as keyword args.  Not sure why, but it was causing 
    weird problems.
    """
    worst = kwargs.get("worst", sausage)
    best = kwargs.get("best", beast)
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
#    if not kwargs.get("invert", False):
#       cmap = matplotlib.cm.get_cmap("jet_r")
#    else:
#        cmap = matplotlib.cm.get_cmap("jet")

    cdict = {
        'red':   ((0.0, 1.0, 1.0),
                  (0.25,1.0, 1.0),
                  (0.5, 0.1, 0.1),
                  (0.75,0.0, 0.0),
                  (1.0, 0.0, 0.0)),
        'green': ((0.0, 1.00,1.00),
                  (0.25,0.95,0.95),
                  (0.5, 0.8, 0.8),
                  (0.75,0.3, 0.3),
                  (1.0, 0.0, 0.0)),
        'blue':  ((0.0, 1.0, 1.0),
                  (0.25,0.75,0.75),
                  (0.5, 0.7, 0.7),
                  (0.75,1.0, 1.0),
                  (1.0, 0.5, 0.5))
    }
    cmap = matplotlib.colors.LinearSegmentedColormap(
        'YellowGreenBlue', cdict, 256)

    norm = matplotlib.colors.Normalize(vmax=best, vmin=worst)

    padleft = 0.15
    padright = 0.10
    figwidth = 1.0 - (padleft + padright)
    axwidth = figwidth / nprobs
    padtop = 0.05
    padbottom = 0.08
    roomforkey = 0.08
    keyheight = 0.02
    figheight = 1.0 - (padtop + padbottom + roomforkey)
    axheight = figheight/nalgos

    print "padleft", padleft
    print "padright", padright
    print "figwidth", figwidth
    print "axwidth", axwidth
    print "padtop", padtop
    print "padbottom", padbottom
    print "roomforkey", roomforkey
    print "keyheight", keyheight
    print "figheight", figheight
    print "axheight", axheight

    sm = matplotlib.cm.ScalarMappable(cmap=cmap) 
    sm.set_array([worst, best])
    cbarposition = [padleft,0,1.0-(padleft+padright),roomforkey]
    ax = fig.add_axes([0, 0, figwidth, keyheight])
    cbax, kw = matplotlib.colorbar.make_axes(ax, orientation="horizontal")
    ax.set_position([padleft, padbottom, figwidth, keyheight])
    ax.text(0.5, -1.7, "hypervolume attainment", ha="center", 
            transform=ax.transAxes)
    cbar = matplotlib.colorbar.Colorbar(ax, sm, **kw)
    fig.delaxes(cbax)

    problemnames = {
        "27_10_1.0": "27 DV",
        "18_10_1.0": "18 DV",
        "27_3_0.1": "27 DV",
        "18_3_0.1": "18 DV"
        }

    for jj in range(nprobs):
        rangex, rangey = ranges[jj]
        for ii in range(nalgos):
            bottom = 1.0-padtop-(ii+1)*axheight
            ax = fig.add_axes([padleft + jj*axwidth, 
                               bottom,
                               axwidth, axheight])
            contour = ax.contourf(meshes[ii][jj], 100, 
                                  cmap=cmap, norm=norm,
                                  rasterized=True)
            #contour.set_rasterized(True)
            tickify(rangex, rangey, ax, nticks)
            if ii == 0:
                ax.set_title(problemnames[problems[jj]])
            else:
                ytl = [tl.get_text() for tl in ax.get_yticklabels()]
                ytl[-1] = ""
                ax.set_yticklabels(ytl)
            if ii == nalgos-1:
                ax.set_xlabel("population size")
            else:
                ax.set_xticklabels([])
                ytl = [tl.get_text() for tl in ax.get_yticklabels()]
                ytl[0] = ""
                ax.set_yticklabels(ytl)
            if jj == nprobs-1:
                ax.text(1.05,0.5,algos[ii],transform=ax.transAxes)
            if jj > 0:
                ax.set_yticklabels([])
    fig.text(0.2*padleft, padbottom + 0.6*figheight, 
             "maximum function evaluations", rotation="vertical",
             ha="center", va="center")

    print "cbarposition", cbarposition
    for ax in fig.axes:
        print ax.get_position()


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

    fig = matplotlib.figure.Figure(figsize=(nproblems*4, nalgos*2.2))
    if args.svg:
        svg.FigureCanvasSVG(fig)
    else:
        agg.FigureCanvasAgg(fig)
    keywords = {}
    keywords["stat"] = args.stat
    keywords["metric"] = args.metric
    keywords["dirname"] = args.stats_directory
    if args.cbar_context_low is not None:
        keywords["context_l"] = args.cbar_context_low
    if args.cbar_context_high is not None:
        keywords["context_h"] = args.cbar_context_high
    if args.best is not None:
        keywords["best"] = args.best
    if args.worst is not None:
        keywords["worst"] = args.worst

    controlmaps(fig, algos, problems, args.params_dir, **keywords)
    fig.subplots_adjust(right=0.87, wspace = 0.03, hspace=0.3)

    fig.savefig(args.output_file)
    
if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
