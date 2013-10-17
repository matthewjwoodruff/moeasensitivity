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

"""

import argparse
import sys
import pandas
import matplotlib
from matplotlib.backends import backend_agg as agg
from matplotlib.backends import backend_svg as svg

class PlottingError(exception): pass

def rerange(intranges):
    """ convert a set of intranges into a list of integers """
    if intranges is None:
        return None
    thelist = []
    for therange in intranges:
        thelist.extend(therange)
    return thelist

def intrange(arg):
    """ convert a command-line argument to a list of integers """
    acceptable_chars = [str(x) for x in range(10)]
    acceptable_chars.append("-")

    partial = []
    first = None

    msg = "Could not convert {0} to index range.".format(arg)
    err = TypeError(msg)

    for char in arg:
        if char not in acceptable_chars:
            raise err
        if char == "-":
            if len(partial) == 0:
                raise err
            elif first is None:
                first = int("".join(partial))
                partial = []
            else: # this means there's a second -, which is not ok
                raise err
        else:
            partial.append(char)

    second = None
    if first is None:
        first = int("".join(partial))
    elif len(partial) == 0:
        raise err
    else:
        second = int("".join(partial))

    if second is None:
        return [first]
    else:
        return range(first, second+1)

def prepare_axes(ax):
    """ set up the axes """
    ax.set_ylim(-0.15,1.1)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xticks([])

def draw_axes(ax, names, limits):
    """ 
    draw the axis lines

    ax: a matplotlib axes for drawing on
    names: a list of names, one for each axis
    limits: a list of tuples, one for each axis, containing the 
            low and high limits for each axis.  These may be strings
            and they probably should because they will use default 
            formatting.
    """
    if len(names) != len(limits):
        raise PlottingError("Different numbers of column names and limits.")

    naxes = len(limits)
    echs = range(naxes)

    # make the axis lines
    ax.set_xticks(echs)
    for tick in ax.get_ticklines(): #make the ticks disappear
        tick.set_color((0,0,0,0))
    ax.vlines(echs, -0.1, 1.1, colors=(0.6,0.6,0.6))

    ax.set_xticklabels(names, rotation=270)

    # label the limits
    for xx in echs:
        ax.text(xx, -0.15, limits[xx][0])
        ax.text(xx, 1.1, limits[xx][1])
 
def draw_lines(ax, table, limits, color)
    """ 
    draw lines for a data set
    ax: a matplotlib axes object
    table: a pandas data table with the data to plot.  
    limits: lower and upper limits for the data
    color: the color to use for data from the table
    """
    xs = range(limits)
    for row in table.itertuples():
        ys = [(x-l)/(h-l) for x, (l, h) in zip(row, limits)]
        ax.plot(xs, ys, color=color)

def draw_legend(ax, names, colors, title):
    """
    first draw lines off the plot to feed the legend,
    then make the legend itself

    ax: a matplotlib axes object for drawing
    """
    for (name, color) in zip(names, colors):
        ll = ax.plot([0,1], [2,2], color=color)

    ax.legend(loc='right', bbox_to_anchor=(naxes+1.4, 0.5),
              bbox_transform=ax.transData, title=title)

def desired_columns(table, columns):
    """
    return a new table with the desired columns in it
    """
    data = {}
    for ii, cc in zip(range(len(columns)), columns):
        data[ii] = table[cc]

    return pandas.DataFrame(data=data)

def find_limits(tables):
    """ find lower and upper limits for each column across all tables """
    mins = tables[0].min()
    maxs = tables[0].max()

    for table in tables:
        for col in table.columns:
            mins[col] = min(table[col].min(), mins[col])
            maxs[col] = max(table[col].max(), maxs[col])

    return zip(mins, maxs)

def init_figures(issplit, isvector):
    """ initialize figures and set up backends """
    if issplit:
        raster = matplotlib.figure(figsize=(9,6))
        agg.FigureCanvasAgg(raster)
        vector = matplotlib.figure(figsize=(9,6))
        svg.FigureCanvasSVG(vector)
    elif isvector:
        vector = matplotlib.figure(figsize=(9,6))
        svg.FigureCanvasSVG(vector)
        raster = vector
    else:
        raster = matplotlib.figure(figsize=(9,6))
        agg.FigureCanvasAgg(raster)
        vector = raster

    return raster, vector

def get_args(argv):
    """ command line arguments """

    parser = argparse.ArgumentParser(argv.pop(0))

    parser.add_argument("files", nargs="+", type=argparse.FileType("r"),
                        help="files containing sets to plot")
    parser.add_argument("-c", "--colors", nargs="+", action='append',
                        help="add a color to the color cycle")
    parser.add_argument("-C", "--columns", type=intrange, nargs="+",
                        help="columns containing data to plot")
    parser.add_argument("-p", "--precision", nargs='+', type=float,
                        help="precision for each column")
    parser.add_argument("-s", "--set-names", nargs='+', type=str,
                        help="names for the sets")
    parser.add_argument("-n", "--names", nargs='+', type=str,
                        help="names for the columns")
    parser.add_argument("-h", "--header", type=int, default=0,
                        help="number of header lines in input files")
    parser.add_argument("-o", "--output-filename", type=str,
                        help="base name for the output file")
    parser.add_argument("-S", "--split", action='store_true',
                        help="produce two output files: a PNG for the "\ 
                             "data, and an SVG for the axes")
    parser.add_argument("-V", "--vector", action='store_true',
                        help="Produce vector output.  WARNING: Will produce "\
                             "very large output files if the input is too large.  "\
                             "More than 50 rows of data, and possibly far fewer, "\
                             "is asking for trouble. Use -S unless you're "
                             "absolutely sure you want this.")

    parser.add_argument("-w", "--wrap", type=int, default=0,
                        help="number of axes to draw before wrapping")

    args = parser.parse_args(argv)
    if args.columns is not None:
        args.columns = rerange(args.columns)

    return args

def cli(argv):
    """ command-line interface """
    args = get_args(argv)
    raster, vector = init_figures(args.split, args.vector)

    tables = [pandas.read_table(f, header=None, skiprows=args.header) 
              for f in args.files]
    for f in args.files:
        f.close()

    tables = [desired_columns(t, args.columns) for t in tables]
    
    limits = find_limits(tables)



