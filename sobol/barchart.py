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

barchart.py
Make a bar chart out of the Sobol' sensitivity indices.
"""

from report import clean
from report import scaleby
from report import scalebetween
import pandas
import argparse
import matplotlib
from matplotlib.backends import backend_agg as agg
from matplotlib.backends import backend_svg as svg

def barchart_figure(fig, table, algos, key=False):
    """
    Make four stacked horizontal barcharts for each
    algorithm.  Put algorithms one after another.
    Draw a key if requested.
    There will be a lot of slack at the top and bottom
    for labels.
    Return the number of bars wide the figure is, so 
    that it can be sized intelligently.
    """
    table = clean(table)

    # determine how many bars wide the figure and subplots are
    counts = table.groupby(["algo", "input"]).count()
    nbars = [len(counts.ix[algo]) for algo in algos]
    total_nbars = sum(nbars)
    if key:
        total_nbars += 2
    nbars = dict(zip(algos, nbars))

    # add objective and decision variable lables
    objlabels = fig.add_axes((0, 0.5, 0.1, 0.4))
    objlabels.set_title("Objectives")
    dvlabels = fig.add_axes((0.1, 0.5, 0.1, 0.4))
    dvlabels.set_title("Decision\nVariables")

    # add actual bar charts
    table = table.set_index(["algo", "problem", "input", "order"])
    xx = 0

    for algo in algos:
        width = float(nbars[algo]) / float(total_nbars)
        left = scalebetween(0.2, 1.0, xx)
        offset = scaleby(0.2,1.0,width)
        ax = fig.add_axes((left, 0.5, offset, 0.4))
        ax.set_title(algo)
        barchart_axes(ax, table.ix[algo])
        xx += width

    return total_nbars

def bar(ax, xx, yy, order, val):
    color = {"Total": (0.2,0.2,0.2), "First": 'w'}[order]
    width = {"Total": 0.8, "First": 0.7}[order]
    zorder = {"Total": 0, "First": 1}[order]
    rect = matplotlib.patches.Rectangle(
        (xx + 0.5*(1.0-width), yy),
        width, val, facecolor = color, edgecolor = (0,0,0,0),
        zorder = zorder)
    ax.add_patch(rect)

def barchart_axes(ax, table):
    """
    expect that table is for a single MOEA, indexed by 
    problem, input, and order
    """
    problems = ["27_3_0.1", "18_3_0.1", "27_10_1.0", "18_10_1.0"]
    inputs = sorted(list(table.index.get_level_values(1).unique()))
    ax.set_xlim((0, len(inputs)))
    ax.set_ylim((0, len(problems)))

    for xx in range(len(inputs)-1):
        ax.axvline(xx+1, color=(0,0,0,0.1))

    yy = 0
    for problem in problems:
        ax.axhline(yy+1, color='k')
        xx = 0
        for inpt in inputs:
            for order in ["First", "Total"]:
                sensitivity = table.xs(problem).xs(inpt).xs(order)
                confidence  = sensitivity["confidence"]
                sensitivity = sensitivity["sensitivity"]

                if sensitivity > confidence and sensitivity > 0:
                    bar(ax, xx, yy, order, sensitivity)
            xx += 1
        yy += 1 

    ax.set_xticks([xx + 0.5 for xx in range(len(inputs))])
    ax.set_xticklabels(inputs, rotation="vertical")
    ax.tick_params(axis="x", bottom=False, top=False)
    ax.set_yticks([])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=argparse.FileType('r'),
                        help = "Table containing Sobol' indices")
    parser.add_argument("algos", 
                        help = "Comma-separated list of MOEAS "\
                               "to include in the plot") 
    parser.add_argument("-k", "--key", action="store_true",
                        help = "Make a key")
    parser.add_argument("-W", "--width", type=float, default=0.25,
                        help = "Width in inches of a bar")
    parser.add_argument("-H", "--height", type=float, default=1.0,
                        help = "Maximum height in inches of a bar.")
    return parser.parse_args()

def cli():
    args = get_args()
    table = pandas.read_table(args.table, sep=' ')
    fig = matplotlib.figure.Figure()
    algos = args.algos.split(",")
    barchart_figure(fig, table, algos, args.key)

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
