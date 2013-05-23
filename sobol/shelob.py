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

===================================================================

shelob.py

Make a bunch of radial convergence plots that, if you have a lot 
of second-order interactions, look like spiderwebs.
"""
import os
import argparse
import radialconvergence as rc
import pandas
import matplotlib
import matplotlib.figure as figure
from  matplotlib.backends.backend_agg import FigureCanvasAgg
from  matplotlib.backends.backend_svg import FigureCanvasSVG

def get_args():
    description = "Make a bunch of radial convergence plots that, "\
                  "if you have a lot of second-order interactions, "\
                  "look like spiderwebs."
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument("algorithms",
                        help="comma-separated list of MOEAs")
    parser.add_argument("problems",
                        help="comma-separated list of problems, "\
                             "e.g. 27_10_1.0")
    parser.add_argument("sensitivities",
                        type = argparse.FileType("r"),
                        help="file in which to find "\
                             "tabulated sensitivity results")
    parser.add_argument("-s", "--stats", default="mean",
                        help = "comma-separated list of stats, "\
                               "default is mean")
    parser.add_argument("-m", "--metrics", default = "Hypervolume",
                        help = "comma-separated list of metrics, "\
                               "default is Hypervolume")
    parser.add_argument("-o", "--output-directory",
                        default="/gpfs/scratch/mjw5407/task1/sobol",
                        help="where to drop the image files")
    parser.add_argument("-n", "--output-name",
                        default = "summary.png",
                        help = "name of the output file")
    parser.add_argument("-V", "--svg", action="store_true",
                        help="use svg format for images (default "\
                             "is png)")
    parser.add_argument("-d", "--dimensions", nargs = 2,
                        default = [22.0,22.0], type=float,
                        help = "width and height of each plot, in "\
                               "centimeters")
    parser.add_argument("-t", "--threshold",
                        default = 0.01, type=float,
                        help="smallest sensitivity index to plot")
    parser.add_argument("-S", "--scale",
                        default = 0.4, type=float,
                        help="scaling factor for elements in plot")
    parser.add_argument("-i", "--individual",
                        action = "store_true",
                        help = "also generate individual figures "\
                               "for each plot.  Always makes one "\
                               "big summary figure by default.")
    parser.add_argument("--threshold-column", default = "L",
                        choices=["L", "E", "H"], 
                        help="apply threshold to this column. "\
                             "L = low end of 95%% CI, E = expected "\
                             "value of sensitivity, H = high end "\
                             "of 95%% CI")


    return parser.parse_args()

def cli():
    args = get_args()
    table = pandas.read_table(args.sensitivities, sep=" ")
    args.sensitivities.close()
    algos = args.algorithms.split(",")
    nalgos = len(algos)
    problems = args.problems.split(",")
    nproblems = len(problems)
    stats = args.stats.split(",")
    nstats = len(stats)
    metrics = args.metrics.split(",")
    nmetrics = len(metrics)

    axdimensions = (args.dimensions[0] / 2.54,
                  args.dimensions[1] / 2.54)
    ncols = nalgos * nmetrics * nstats
    nrows = nproblems 
    figdimensions = (axdimensions[0] * ncols,
                     axdimensions[1] * nrows)
   
    fig = figure.Figure(figsize = figdimensions)
    if args.svg:
        FigureCanvasSVG(fig)
    else:
        FigureCanvasAgg(fig)

    #for pp, mm, ss, aa in itertools.product( range(nproblems), 
            #range(nmetrics), range(nstats), range(nalgos)):
    for mm in range(nmetrics):
        for pp in range(nproblems):
            for ss in range(nstats):
                for aa in range(nalgos):
                    index = aa + ss * nalgos + pp * nstats * nalgos\
                            + mm * nproblems * nstats * nalgos + 1
                    ax = fig.add_subplot(nrows, ncols, index, frameon=False)
                    title = []
                    if nalgos > 1:
                        title.append(algos[aa])
                    if nproblems > 1:
                        dv, obj, eps = problems[pp].split("_")
                        title.append(dv + " Variables,")
                        title.append(obj + " Objectives")
                    if nstats > 1:
                        title.append(stats[ss])
                    if nmetrics > 1:
                        title.append(metrics[mm])
                    title = " ".join(title)
                    rc.spider(algos[aa], problems[pp], stats[ss], 
                              metrics[mm], table, 
                              ax, threshold = args.threshold,
                              scale = args.scale, 
                              threshold_column = args.threshold_column,
                              title = title)
                    if args.individual:
                        fig2 = figure.Figure( figsize=axdimensions)
                        ax = fig2.add_subplot(1,1,1,frameon=False)
                        if args.svg:
                            FigureCanvasSVG(fig2)
                        else:
                            FigureCanvasAgg(fig2)
                        rc.spider(algos[aa], problems[pp], stats[ss], 
                              metrics[mm], table, 
                              ax, threshold = args.threshold,
                              scale = args.scale)
                        fn = "{0}_{1}_{2}_{3}".format( algos[aa], 
                               problems[pp], stats[ss], metrics[mm])
                        fn = os.path.join(args.output_directory, fn)
                        fig2.savefig(fn)
                        

    fig.subplots_adjust(hspace=0.1,wspace=0, top=0.98, bottom=0.05,
                        left=0.00, right=1.00)
    fig.savefig(os.path.join(args.output_directory, 
                             args.output_name))

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
