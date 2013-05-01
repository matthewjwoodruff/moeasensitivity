import os
import re
import sys
import argparse

import math
import numpy
import pandas
import matplotlib
import matplotlib.patches as patches
import matplotlib.lines as lines
import matplotlib.backends.backend_svg as svg
import matplotlib.backends.backend_agg as agg

def totalorder(row, ax, centers, smallest=0.03):
    scale = 0.4
    center = centers[row['input']]
    #ax.annotate(row['input'], center, arrowprops={'arrowstyle':'-'})

    radius = row['sensitivity'] + row['confidence']
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(1.0,0.0,0.0),lw=0))

    xx = center[0] + radius*center[0]
    yy = center[1] + radius*center[1]
    xx = 1.2 * center[0]
    yy = 1.2 * center[1]

    if center[0] < -0.1:
        halignment = "right"
    elif center[0] > 0.1:
        halignment = "left"
    else:
        halignment = "center"

    if center[1] < -0.1:
        valignment = 'top'
    elif center[1] > 0.1:
        valignment = 'bottom'
    else: 
        valignment = "baseline"

    text = ax.text(xx, yy, row['input'],
                   horizontalalignment=halignment,
                   verticalalignment=valignment)

    radius = row['sensitivity'] 
    if radius < smallest: return
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(0.8,0.6,0.6),lw=0))

    radius = row['sensitivity'] - row['confidence']
    if radius < smallest: return
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(1.0,1.0,1.0),lw=0))


def firstorder(row, ax, centers, smallest=0.03):
    scale = 0.4
    center = centers[row['input']]
    #ax.annotate(row['input'], center, arrowprops={'arrowstyle':'-'})

    radius = row['sensitivity'] + row['confidence']
    if radius < smallest: return
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(0.1,0.1,0.6),lw=0))

    radius = row['sensitivity'] 
    if radius < smallest: return
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(0.6,0.6,0.8),lw=0))

    radius = row['sensitivity'] - row['confidence']
    if radius < smallest: return
    radius *= scale
    ax.add_patch(patches.Ellipse(center,
        radius, radius, facecolor=(0.3,0.3,1),lw=0))

def secondorder(row, ax, centers, smallest=0.03):
    # don't draw at all if ci includes 0
    if row['sensitivity'] - row['confidence'] < 0:
        return
    x1, y1 = centers[row['input']]
    x2, y2 = centers[row['interaction']]
    dy = y2-y1
    dx = x2-x1
 
    angle = math.atan2(dx, dy)
    length = math.sqrt(dx**2+dy**2)

    transform = matplotlib.transforms.Affine2D()
    transform.rotate(-angle)
    transform.translate(x1,y1)

    scale = 0.8

    sens = row['sensitivity'] + row['confidence']
    if sens < smallest: return
    width = scale * sens

    widthtransform = matplotlib.transforms.Affine2D().translate(
            -0.5*width,0)

    ax.add_patch(patches.Rectangle((0,0), width, length,
        linewidth=0, transform = widthtransform + transform + 
            ax.transData,
            facecolor=[0.8,0.8,1]))

    sens = row['sensitivity'] 
    if sens < smallest: return
    width = scale * sens

    widthtransform = matplotlib.transforms.Affine2D().translate(
            -0.5*width,0)

    ax.add_patch(patches.Rectangle((0,0), width, length,
        linewidth=0, transform = widthtransform + transform + 
            ax.transData,
            facecolor=[0.4,0.4,1]))

    sens = row['sensitivity'] - row['confidence']
    if sens < smallest: return
    width = scale * sens

    widthtransform = matplotlib.transforms.Affine2D().translate(
            -0.5*width,0)

    ax.add_patch(patches.Rectangle((0,0), width, length,
        linewidth=0, transform = widthtransform + transform + 
            ax.transData,
            facecolor=[0,0,1]))

def spiderplot(ser, ax, centers):
    ser[ser['order'] == 'Second'].apply(
            secondorder, axis=1, args=(ax, centers))
    ser[ser['order'] == 'Total'].apply(
            totalorder, axis=1, args=(ax, centers))
    ser[ser['order'] == 'First'].apply(
            firstorder, axis=1, args=(ax, centers))

def do_plots(args):
    ser = pandas.read_table(args.table)

    fig = matplotlib.figure.Figure(figsize=(13.33, 5))
    canvas = svg.FigureCanvasSVG(fig)
    #canvas = agg.FigureCanvasAgg(fig)

    # figure out where the nodes go. How many inputs?
    inputs = ser.groupby(['input']).groups.keys()
    inputs.sort()
    angle = 2 * math.pi / len(inputs)
    centers = {}
    for ii in range(len(inputs)):
        centers[inputs[ii]] = (math.cos(ii*angle), math.sin(ii*angle))

    # figure out how many plots to make and how to arrange them
    print ser
    ser = ser[ser['response'] == args.response]
    print ser

    plots = ser.groupby(['tag', 'response']).groups.keys()

    nplots = len(plots)
    tags, responses = zip(*plots)
    # is there a better way to uniquify a list in python?
    responses = list(set(responses))
    tags = list(set(tags))

    # do we have data formatted for comparison?
    if len(responses) * len(tags) == len(plots):
        ncols = len(tags)
        nrows = len(responses)
    else: 
        ncols = 1
        nrows = len(plots)

    def compare_by_second(xx, yy):
        if xx[1] < yy[1]:
            return -1
        if xx[1] > yy[1]:
            return 1
        return cmp(xx[0], yy[0])

    plots.sort(cmp = compare_by_second)
    counter = 1
    for plot in plots:
        ax = fig.add_subplot(nrows, ncols, counter, frameon=False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.2, 1.2)
        response = plot[1]
        tag = plot[0]
        filt = (ser['response']==response) & (ser['tag']==tag)
        spiderplot(ser[filt], ax, centers)
#        if counter <= ncols:
#            ax.set_xlabel(response)
#            ax.get_xaxis().set_label_position('top')
#            ax.set_title(tag)
#        if counter % ncols == 1 and len(tags) > 1:
#            ax.set_ylabel(response.upper())
        counter += 1

    return fig

def cli():
    description = sys.argv[0] \
                  + ": create interaction plots based on "\
                  + "a table of sensitivity indices"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("table", type=argparse.FileType('r'))
    parser.add_argument("response")
    args = parser.parse_args()

    # make the plots
    fig = do_plots(args)

    # write the output
    fig.savefig("spiders_{0}".format(args.response))


if __name__ == "__main__":
    cli()
# vim:sw=4:ts=4:expandtab:fdm=indent:colorcolumn=68:ai
