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

report.py
Make a report out of the Sobol' sensitivity indices.
"""

import argparse
import StringIO
import pandas
import matplotlib
from matplotlib.backends import backend_agg as agg
import numpy

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=argparse.FileType('r'),
                        help="Table containing Sobol' indices")
    return parser.parse_args()

def clean(table):
    sub = table[table["order"] != "Second"]
    sub = sub[sub["algo"] != "BorgRecency"]
    if "interaction" in sub.columns.values:
        del sub["interaction"]
    if "stat" in sub.columns.values:
        sub = sub[sub["stat"] == "mean"]
        del sub["stat"]
    if "metric" in sub.columns.values:
        sub = sub[sub["metric"] == "Hypervolume"]
        del sub["metric"]
    return sub

def report(table):
    sub = clean(table)
    indexed = sub.set_index(["algo", "problem", "input", "order"])
    mask1 = pandas.DataFrame(
        indexed["sensitivity"] - indexed["confidence"] < 0)
    mask2 = pandas.DataFrame( indexed["sensitivity"] < 0)

    del indexed["confidence"]

    masked = indexed.mask(mask1).mask(mask2)
    report = masked.unstack(["problem", "order"])
    return report

def barchart(ax, rept):
    columns = rept.columns
    nrows = len(rept)
    ncols = len(columns) / 2
    irow = 1
    ylabels = [""] * nrows
    xlabels = [""] * ncols
    oalgo = ""
    for algo, param in rept.index.values:
        icol = -1
        yy = nrows - irow
        if algo != oalgo:
            ax.axhline(yy+1, color = 'k')
        oalgo = algo    
        ylabels[yy] = param

        oproblem = ""
        for ss, problem, order in columns:
            if problem != oproblem:
                icol += 1
            oproblem = problem
            xlabels[icol] = {"27_10_1.0": "27 DV", "18_10_1.0": "18 DV", "27_3_0.1": "27 DV", "18_3_0.1": "18 DV"}[problem]
            sensitivity = rept.ix[(algo, param), (ss, problem, order)]
            color = {"Total": (0.2,0.2,0.2), "First": 'w'}[order]
            width = {"Total": 0.8, "First": 0.7}[order]
            zorder = {"Total": 0, "First": 1}[order]
            if not numpy.isnan(sensitivity):
                xy = (yy, icol)
                rect = matplotlib.patches.Rectangle(
                    (icol, yy+0.5*(1.0-width)), 
                    sensitivity, width, 
                    facecolor = color, edgecolor=(0,0,0,0),
                    zorder=zorder)
                ax.add_patch(rect)
        irow += 1    
    ax.set_xlim((0, ncols))
    ax.set_ylim((0, nrows))
    ax.set_yticks([val + 0.5 for val in range(nrows)])
    ax.set_yticklabels(ylabels)
    ax.set_xticks([val + 0.5 for val in range(ncols)])
    ax.set_xticklabels(xlabels)
    for xx in range(ncols):
        ax.axvline(xx, color='k')

def scaleby(lo, hi, xx):
    """
    return a number that is x proportion to the difference
    between lo and hi
    """
    return xx * (hi-lo)

def scalebetween(lo, hi, xx):
    """
    return a number that's x into the interval between 
    lo and hi, where x is between 0 and 1
    """
    return xx * (hi-lo) + lo

def multibarchart(fig, table):
    table = clean(table)
    algos = ["Borg", "eMOEA", "NSGAII", "eNSGAII", "GDE3"]
    problemgroups = [("3 Objective", ["27_3_0.1", "18_3_0.1"]),
                     ("10 Objective", ["27_10_1.0", "18_10_1.0"])]
    nrows = len(algos)
    ncols = len(problemgroups)
    counter = 0
    width = 0.5
    condition = lambda algo: table[(table["algo"] == algo) & (table["order"] != "Second")]
    totalrows = sum([len(condition(algo)) for algo in algos])
    yy = 1.0
    ylo = 0.05
    yhi = 0.98
    xlo = 0.4
    xhi = 0.98
    for algo in algos:
        talgo = table[table["algo"] == algo]
        height = float(len(talgo)) / totalrows 
        yy -= height
        xx = 0.0

        fig.text(0.03, scalebetween(ylo, yhi, yy + height/2), 
                 algo, rotation='vertical')

        for problemgroup in problemgroups:
            counter += 1
            ax = fig.add_axes((scalebetween(xlo, xhi, xx), 
                               scalebetween(ylo, yhi, yy), 
                               scaleby(xlo, xhi, width), 
                               scaleby(ylo, yhi, height)))
            condition = talgo["problem"].apply(
                lambda prob: prob in problemgroup[1])
            tgroup = talgo[condition]
            barchart(ax, report(tgroup))
            if counter <= ncols * (nrows -1):
                ax.set_xticklabels([])
            else:
                ax.set_xlabel(problemgroup[0])
            if counter % ncols != 1:
                ax.set_yticklabels([])
            xx += width

def cli():
    args = get_args()
    table = pandas.read_table(args.table, sep=" ")
    fig = matplotlib.figure.Figure(figsize=(6,15))
    agg.FigureCanvasAgg(fig)
    multibarchart(fig, table)
    fig.savefig("report")


if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
