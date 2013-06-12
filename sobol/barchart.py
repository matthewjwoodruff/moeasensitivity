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

def make_labels(ax, labels):
    """
    Draw the labels as follows:
    two labels: 1/4, 3/4
    three labels: 1/6, 3/6, 5/6
    four labels: 1/8, 3/8, 5/8, 7/8
    five labels: 1/10, 3/10, 5/10, 7/10, 9/10
    """
    denominator = 2.0 * len(labels)
    fractions = [(2.0*xx + 1) / denominator
                 for xx in range(len(labels))]
    for label, yy in zip(labels, fractions):
        ax.text(0.5, yy, label, 
                horizontalalignment="center",
                verticalalignment="center",
                rotation="vertical", size="small")
    ax.set_yticks([])

    step = 1.0 / float(len(labels))
    for yy in range(1, len(labels)):
        ax.axhline(yy * step, color = 'k')

def draw_key(ax):
    """
    Make a key
    """
    ax.set_xlim((0,3))
    ax.set_ylim((0,4))
    ax.set_xticks([])
    ax.set_yticks([])

    colors = {"Total": (0.2,0.2,0.2), "First": (0.9,0.9,0.9)}
    widths = {"Total": 0.8, "First": 0.6}
    zorders = {"Total": 0, "First": 1}

    x1 = 2
    x2 = 0
    for order, val in [("First", 0.6), ("Total", 0.8)]:
        rect = matplotlib.patches.Rectangle(
            (0.6, 1.5),
            #(1-widths[order]/2, 1.5),
            widths[order], val, facecolor=colors[order], 
            edgecolor=(1,1,1),
            zorder = zorders[order])
        x1 = min(x1, 1-widths[order]/2)
        x1 = 0.6
        #x2 = max(x2, 1+widths[order]/2)
        x2 = max(x2, 0.3+widths[order])
        ax.add_patch(rect)
    line = matplotlib.lines.Line2D([x1,x2], [1.5,1.5], color='k')
    #ax.add_line(line)
    ax.set_frame_on(False)
    ax.annotate("Total\nOrder", (0.8, 2.3), xytext=(1.1, 2.65),
                horizontalalignment="baseline",
                arrowprops={"width":0.3, "shrink":0.05,
                            "frac": 0.1, "headwidth":4})
    ax.annotate("First\nOrder", (0.8, 1.6), xytext=(1.1, 1.0),
                horizontalalignment="baseline",
                arrowprops={"width":0.3, "shrink":0.05,
                            "frac": 0.1, "headwidth":4})
    ax.text(1.3, 3.15, "Key", horizontalalignment="center",
            weight="bold")
    rect = matplotlib.patches.Rectangle((0.25, 0.8), 2.3, 2.6,
                facecolor='w', edgecolor='k', zorder=-1)
    ax.add_patch(rect)
        

def barchart_figure(fig, table, algos, key=False, **kwargs):
    """
    Make four stacked horizontal barcharts for each
    algorithm.  Put algorithms one after another.
    Draw a key if requested.
    There will be a lot of slack at the top and bottom
    for labels.
    """
    table = clean(table)

    # determine how many bars wide the figure and subplots are
    counts = table.groupby(["algo", "input"]).count()
    nbars = [len(counts.ix[algo]) for algo in algos]
    total_nbars = sum(nbars)
    total_nbars += 1 # for the labels on the left
    if key:
        total_nbars += 3
    nbars = dict(zip(algos, nbars))

    wbar = 1.0 / total_nbars

    # add objective and decision variable lables
    objlabels = fig.add_axes((0, 0.5, 0.5*wbar, 0.4))
    make_labels(objlabels, ["10 Objectives", "3 Objectives"])
    objlabels.set_xticks([])
    objlabels.tick_params(axis="x", bottom=False, top=False)

    dvlabels = fig.add_axes((0.5*wbar, 0.5, 0.5*wbar, 0.4))
    make_labels(dvlabels, ["18 DV", "27 DV", "18 DV", "27 DV"])
    dvlabels.set_xticks([])
    dvlabels.tick_params(axis="x", bottom=False, top=False)

    # add actual bar charts
    table = table.set_index(["algo", "problem", "input", "order"])
    xx = wbar # offset for the labels on the left

    for algo in algos:
        width = nbars[algo] * wbar
        ax = fig.add_axes((xx, 0.5, width, 0.4))
        ax.set_title(algo, weight="bold")
        barchart_axes(ax, table.ix[algo])
        xx += width

    if key:
        ax = fig.add_axes((xx, 0.5, 3*wbar, 0.4))
        draw_key(ax)

    # adjust bar width and height
    barwidth = kwargs.get("barwidth", 0.4)
    barheight = kwargs.get("barheight", 1.3)
    fig.set_figwidth(total_nbars * barwidth)
    fig.set_figheight(10*barheight)

def bar(ax, xx, yy, order, val):
    color = {"Total": (0.2,0.2,0.2), "First": (0.9,0.9,0.9)}[order]
    width = {"Total": 0.8, "First": 0.6}[order]
    zorder = {"Total": 0, "First": 1}[order]
    rect = matplotlib.patches.Rectangle(
        #(xx + 0.5*(1.0-width), yy),
        (xx + 0.1, yy),
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
    ax.set_xticklabels(inputs, rotation="vertical", size="small" )
    for tl in ax.xaxis.get_majorticklabels():
        pos = tl.get_position()
        pos = (pos[0], -0.0025)
        tl.set_position(pos)
    ax.tick_params(axis="x", bottom=False, top=False)
    ax.set_yticks([])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("table", type=argparse.FileType('r'),
                        help = "Table containing Sobol' indices")
    parser.add_argument("algos", 
                        help = "Comma-separated list of MOEAS "\
                               "to include in the plot") 
    parser.add_argument("output", help="name of image file to write")
    parser.add_argument("-k", "--key", action="store_true",
                        help = "Make a key")
    parser.add_argument("-W", "--width", type=float, default=0.25,
                        help = "Width in inches of a bar")
    parser.add_argument("-H", "--height", type=float, default=1.0,
                        help = "Maximum height in inches of a bar.")
    parser.add_argument("-v", "--vector", action="store_true",
                        help = "Write SVG instead of PNG output")
    return parser.parse_args()

def cli():
    args = get_args()
    table = pandas.read_table(args.table, sep=' ')
    fig = matplotlib.figure.Figure()
    if args.vector:
        svg.FigureCanvasSVG(fig)
    else:
        agg.FigureCanvasAgg(fig)
    
    algos = args.algos.split(",")
    barchart_figure(fig, table, algos, args.key,
                    barwidth=args.width,
                    barheight=args.height)
    fig.savefig(args.output)

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
