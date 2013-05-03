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

radialconvergence.py
"""
import argparse
import matplotlib
import matplotlib.figure as figure
from  matplotlib.backends.backend_agg import FigureCanvasAgg
from  matplotlib.backends.backend_svg import FigureCanvasSVG
import pandas
import math
import copy
import itertools
import os

def get_args():
    description = "Radial convergence plots for Sobol' global "\
                  "sensitivity indices, for MOEA parameterization "\
                  "study.  Data must be in a table such as that "\
                  "produced by tabulate.py"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("algorithm",
                        help="which MOEA to plot, e.g. eMOEA")
    parser.add_argument("problem",
                        help="which problem to plot, e.g. 27_3_1.0")
    parser.add_argument("statistic",
                        help="which statistic to plot, e.g. q50")
    parser.add_argument("metric",
                    help="which metric to plot, e.g. Hypervolume")
    parser.add_argument("table", type = argparse.FileType("r"),
                        help="table of sensitivity indices like "\
                             "that produced by tabulate.py")
    parser.add_argument("-o", "--output-dir", 
                        help = "where to put the image file "\
                               "produced by this script. "\
                               "defaults to the current directory",
                        default = ".")
    parser.add_argument("-s", "--svg",
                        help = "produce an svg instead of a png",
                        action = "store_true")
    parser.add_argument("-d", "--dimensions", nargs = 2,
                        default = [18.0,18.0], type=float,
                        help = "width, height of the figure, in "\
                               "centimeters")
    parser.add_argument("-t", "--threshold",
                        default = 0.03, type=float,
                        help="smallest sensitivity index to plot")
    parser.add_argument("-S", "--scale",
                        default = 0.4, type=float,
                        help="scaling factor for elements in plot")
    return parser.parse_args()

def filename(algo, problem, stat, metric):
    return "rcp_{0}_{1}_{2}_{3}".format(algo, problem, stat, metric)

def format_axes(ax):
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_xticks([])
    ax.set_yticks([])

def circle(ax, angle, rr, cc):
    ax.add_patch(matplotlib.patches.Ellipse(
                    (math.cos(angle), math.sin(angle)), 
                     rr, rr, facecolor=cc, lw=0))

def data_for(table, algo, problem, stat, metric):
    data = table[(table["algo"] == algo) & \
                 (table["problem"] == problem) & \
                 (table["stat"] == stat) & \
                 (table["metric"] == metric)]
    data = copy.copy(data)
    data["lo"] = data["sensitivity"] - data["confidence"]
    data["hi"] = data["sensitivity"] + data["confidence"]
    return data

def parameters_in(data):
    parameters = data.groupby("input").groups.keys()
    parameters.sort()
    return parameters

def angles_for(parameters):
    angle = 2 * math.pi / len(parameters)
    angles = [angle * ii + math.pi / 8.3 
              for ii in range(len(parameters))]
    angles = dict(zip(parameters, angles))
    return angles

def stripe(ax, p1, p2, width, color):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    angle = math.atan2(dx, dy)
    length = math.sqrt(dx**2 + dy**2)

    transform = matplotlib.transforms.Affine2D()
    transform.translate(-0.5*width, 0) # center the stripe
    transform.rotate(-angle)
    transform.translate(x1, y1)

    ax.add_patch(matplotlib.patches.Rectangle(
                 (0,0), width, length, linewidth=0, 
                 transform=transform + ax.transData,
                 facecolor=color))

def get_endpoints(angles, row):
    x1 = math.cos(angles[row[1]["input"]])
    y1 = math.sin(angles[row[1]["input"]])
    x2 = math.cos(angles[row[1]["interaction"]])
    y2 = math.sin(angles[row[1]["interaction"]])
    return (x1, y1), (x2, y2)

def text(ax, angle, name, offset):
    radius = 1.0 + offset
    fudgefactor = 1.1
    radius = max(radius, fudgefactor)
    x1 = radius * math.cos(angle)
    y1 = radius * math.sin(angle)
    dangle = angle * 180.0 / math.pi
    transform = matplotlib.transforms.Affine2D()
    transform.translate(radius, 0)
    transform.rotate(angle)
    transform=transform + ax.transData
    if (dangle < 90 and dangle > -90) or dangle > 270:
        text = ax.text(0, 0, name,
                       verticalalignment="center",
                       horizontalalignment="left",
                       rotation_mode="anchor",
                       rotation = dangle,
                       transform=transform)
    else:
        text = ax.text(0, 0, name,
                       verticalalignment="center",
                       horizontalalignment="right",
                       rotation_mode="anchor",
                       rotation = 180+dangle,
                       transform=transform)
    
    return text

    
def spider(algo, problem, stat, metric, table, ax, **kwargs):
    scale = kwargs.get("scale", 0.4)
    threshold = kwargs.get("threshold", 0.03)
    data = data_for(table, algo, problem, stat, metric)
    format_axes(ax)
    ax.set_title("{0} {1} {2} {3}".format(
                    algo, problem, stat, metric, table))

    parameters = parameters_in(data)
    angles = angles_for(parameters)

    # second order
    columns = ["hi", "sensitivity", "lo"]
    colors = [(0.8, 0.8, 1.0), (0.4, 0.4, 1.0), (0.0, 0.0, 1.0)]
    secondorder = data[data["order"] == "Second"]
    for row in secondorder.iterrows():
        if row[1]["lo"] > threshold:
            for column, color in zip(columns, colors):
                p1, p2 = get_endpoints(angles, row)
                width = scale * row[1][column]
                stripe(ax, p1, p2, width, color)


    # total order and text
    totalorder = data[data["order"] == "Total"]
    colors = [(1.0, 0.0, 0.0), (0.8, 0.6, 0.6), (1.0, 1.0, 1.0)]
    for row in totalorder.iterrows():
        name = row[1]["input"]
        angle = angles[name]
        if row[1]["lo"] > threshold:
            for column, color in zip(columns, colors):
                circle(ax, angle, scale * row[1][column], color)
        text(ax, angle, name, row[1]["lo"] * scale)

    # first order
    firstorder = data[data["order"] == "First"]
    colors = [(0.1,0.1,0.6), (0.6,0.6,0.8), (0.3,0.3,1.0)]
    for row in firstorder.iterrows():
        if row[1]["lo"] > threshold:
            for column, color in zip(columns, colors):
                circle(ax, angles[row[1]["input"]],
                            scale * row[1][column], color)

def cli():
    args = get_args()

    fig = matplotlib.figure.Figure(figsize = (
            args.dimensions[0]/2.54, args.dimensions[1]/2.54) )
    ax = fig.add_subplot(1,1,1,frameon=False)
    if args.svg:
        FigureCanvasSVG(fig)
    else:
        FigureCanvasAgg(fig)

    table = pandas.read_table(args.table, sep=" ")
    args.table.close()
    spider(args.algorithm, args.problem, args.statistic, 
           args.metric, table, ax)

    fn = filename(args.algorithm, args.problem, 
                                     args.statistic, args.metric)
    if args.svg:
        fn = fn + ".svg"
    else:
        fn = fn + ".png"
    fig.savefig(os.path.join(args.output_dir, fn))

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
