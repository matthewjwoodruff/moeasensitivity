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
cdf.py
In: hv data
Out: CDF plots
"""
import argparse
import pandas
import matplotlib
# svg is not realistic due to the number of points being plotted
from matplotlib.backends import backend_agg as agg
import numpy

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("objectives",
                        choices = ["10_1.0", "3_1.0", "3_0.1"],
                        help = "objective_eps combination to plot")
    parser.add_argument("-f", "--format",
                        choices = ["cdf", "shaded", "both"],
                        default = "shaded",
                        help = "do a CDF plot, a shaded plot, or both")
    parser.add_argument("-o", "--output",
                        help = "name of the output file",
                        default="cdf")
    parser.add_argument("-a", "--algorithms",
                        help = "comma separated list of algorithms "\
                               "to plot", 
                        default = "Borg,eMOEA,NSGAII,eNSGAII,GDE3")
    return parser.parse_args()

def cdf(fig, objectives, algorithms):
    algos = ["Borg", "BorgRecency", "eMOEA", 
             "NSGAII", "eNSGAII", "GDE3"]
    dvs = ["27", "18"]
    nrows = len(dvs)
    ncols = len(algos)

    counter = 0
    best = float("-inf")
    for ndv in dvs:
        for algo in algos:
            counter += 1
            ax = fig.add_subplot(nrows, ncols, counter)
            hv = pandas.read_table("/gpfs/scratch/mjw5407/task1/stats/Set_mean_{0}_{1}_{2}".format(algo, ndv, objectives), sep=" ")
            hv.sort(["Hypervolume"], inplace=True)
            best = max(best, hv.Hypervolume.max())
            ax.plot(hv.Hypervolume, linewidth=4)
            xmax = len(hv)
            ax.set_xlim(0, xmax)
            places = [0.2, 0.5, 0.8]
            tix = [ratio * xmax for ratio in places]
            ax.set_xticks(tix)
            if counter > (nrows - 1) * ncols:
                ax.set_xticklabels(["{0:.0f}".format(100*place) for place in places])
                ax.set_xlabel("Percentile")
            else:
                ax.set_xticklabels([])
                ax.set_title(algo)
            if counter % ncols == 1:
                ax.set_ylabel("{0} DV Attainment".format(dvs[counter // ncols]))
    
    counter = 0
    for ndv in dvs:
        for algo in algos:
            ax = fig.axes[counter]
            counter += 1
            ax.set_ylim(0, best)
            places = [0.25, 0.5, 0.75]
            tix = [ratio * best for ratio in places]
            ax.set_yticks(tix)
            if counter % ncols == 1:
                ax.set_yticklabels(["{0:.2f}".format(place)
                                    for place in places])
            else:
                ax.set_yticklabels([])

    fig.subplots_adjust(hspace=0,wspace=0)

def shady(fig, objectives):
    algos = ["Borg", "BorgRecency", "eMOEA", 
             "NSGAII", "eNSGAII", "GDE3"]
    dvs = ["27", "18"]
    nrows = len(dvs)
    ncols = len(algos)

    counter = 0
    best = float("-inf")
    hvs = []
    for ndv in dvs:
        for algo in algos:
            hv = pandas.read_table("/gpfs/scratch/mjw5407/task1/stats/Set_mean_{0}_{1}_{2}".format(algo, ndv, objectives), sep=" ")
            hvs.append(hv)
            best = max(best, hv.Hypervolume.max())

    # compute bins
    step = 0.005*best
    bins = numpy.arange(0, best, step)

    counter = 0
    for ndv in dvs:
        for algo in algos:
            hv = hvs[counter]
            total = float(len(hv))
            counter += 1
            print nrows, ncols, counter
            ax = fig.add_subplot(nrows, ncols, counter, frameon=False)

            for abin in bins:
                subset = hv[hv.Hypervolume > abin]
                size = len(subset)
                bincolor = 1.0 - size/total
                bincolor = (bincolor, bincolor, bincolor)
                rect = matplotlib.patches.Rectangle(
                                (0,abin), 1, step,
                                facecolor = bincolor,
                                linewidth=0)
                ax.add_patch(rect)

            ax.plot([0.5], [hv.Hypervolume.max()], "o", color='k')

            ax.set_xlim(0, 1)
            if counter-1 > ncols:
                ax.set_title(algo)
            if counter % ncols == 1:
                ax.set_ylabel("{0} DV Attainment".format(dvs[counter // ncols]))
    
            ax.set_xticks([])
            ax.set_xticklabels([])
            ax.set_ylim(0, best)
            places = [0, 0.2, 0.4, 0.6, 0.8]
            tix = [ratio * best for ratio in places]
            ax.set_yticks(tix)
            ax.hlines(tix, 0, 1)
            if counter % ncols == 1:
                ax.set_yticklabels(["{0:.0f}".format(100*place)
                                    for place in places])
            else:
                ax.set_yticklabels([])

    fig.subplots_adjust(hspace=0,wspace=0)

def get_tables(algos, dvs, objectives):
    hvs = []
    for ndv in dvs:
        for algo in algos:
            hv = pandas.read_table("/gpfs/scratch/mjw5407/task1/stats/Set_mean_{0}_{1}_{2}".format(algo, ndv, objectives), sep=" ")
            hvs.append(hv)
    return hvs

def shaded(fig, objectives, algos, dvs, sidebyside):
    xsize = len(algos)
    if sidebyside == True:
        nrows = 1
        ncols = len(dvs)
    else:
        nrows = len(dvs)
        ncols = 1

    hvs = get_tables(algos, dvs, objectives)
    best = max([hv.Hypervolume.max() for hv in hvs])

    step = 0.005*best
    bins = numpy.arange(0, best, step)

    counter = 0
    places = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    tix = [ratio * best for ratio in places]
    
    for dv in dvs:
        xx = 0
        counter += 1
        ax = fig.add_subplot(nrows, ncols, counter)
        for algo in algos:
            index = (counter -1) * len(algos) + xx
            hv = hvs[index]
            total = float(len(hv))
            for abin in bins:
                subset = hv[hv.Hypervolume > abin]
                size = len(subset)
                bincolor = 1.0 - size/total
                bincolor = (bincolor, bincolor, bincolor)
                rect = matplotlib.patches.Rectangle(
                            (xx, abin), 1, step,
                            facecolor = bincolor,
                            linewidth=0)
                ax.add_patch(rect)
            
            ax.plot([xx+0.5], [hv.Hypervolume.max()], "o", color="k")
            xx += 1

        ax.set_xlim(0, len(algos))
        ax.set_xticks([tt + 0.5 for tt in range(len(algos))])
        ax.set_xticklabels(algos, rotation=45, ha='right')
        if counter < nrows and not sidebyside :
            ax.set_xticks([])
            ax.set_xticklabels([])
        
        ax.set_ylim(0, 1.05*best)
        ax.set_yticks(tix)
        ax.hlines(tix, 0, len(algos), color=(0.5,0.5,0.5))
        if sidebyside:
            ax.set_title("{0} Decision Variables".format(dv))
        else:
            ax.set_ylabel("Percent of Best Hypervolume")
            ax.text(1.02*len(algos), 0.5, 
                        "{0} Decision Variables".format(dv),
                        rotation = 270)

        if counter == 1 and sidebyside:
            ax.set_yticklabels(["{0:.0f}".format(100*val) 
                            for val in places])
            ax.set_ylabel("Percent of Best Hypervolume")
        elif counter > 1 and sidebyside:
            ax.set_yticks([])
            ax.set_yticklabels([])
    fig.subplots_adjust(hspace=0.05, wspace=0.05)

def cli():
    args = get_args()
    fig = matplotlib.figure.Figure()
    agg.FigureCanvasAgg(fig)
    algos = args.algorithms.split(",")
    dvs = ["27", "18"]
    if args.format == "cdf":
        cdf(fig, args.objectives, algos)
        fig.set_figwidth(8)
        fig.set_figheight(12)
        fig.savefig(args.output)
    elif args.format == "shaded":
        fig.set_figwidth(6)
        fig.set_figheight(12)
        shaded(fig, args.objectives, algos, dvs, True)
        fig.savefig(args.output)
    elif args.format == "both":
        print "both not implemented yet, falling back to shaded"
        shady(fig, args.objectives)
        fig.savefig(args.output)
        
if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
