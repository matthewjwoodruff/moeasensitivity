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

Coming in: one of 36 algo/problem combinations. 50 seeds in
one file.  Also the _Sobol file specifying the 
parameterization for each row, as well as the parameters
file itself.
Going out: stats: mean, quantile, variance
           grouped by parameterization
           grouped by some or all 2d combinations of 
           parameters
           
"""
import argparse
import pandas
import numpy
import re
import os
import copy

def is_quantile(stat):
    return re.match("q[0-9][0-9]?$", stat)

def is_stat(stat):
    if stat in ["mean", "variance", "min", "max", "q100"]:
        return stat
    elif is_quantile(stat):
        return stat
    else:
        raise argparse.ArgumentTypeError(
                "Invalid statistic {0}".format(stat))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", 
                        type=argparse.FileType("r"),
                        help="data file to be summarized."
                             "Should have columns seed, "\
                             "set, and metrics columns.")
    parser.add_argument("parameterizations",
                        type=argparse.FileType("r"),
                        help="file containing parameter"\
                             "izations.  Number of param"\
                             "eterizations should be the "\
                             "same as number of rows per "\
                             "seed in the data file."
                       )
    parser.add_argument("parameters",
                        type=argparse.FileType("r"),
                        help="file describing parameters. "\
                             "Should have as many rows as "\
                             "parameterizations file has "\
                             "columns."
                       )
    stats = ["mean", "variance", "q10", "q50", "q90"]
    parser.add_argument("-s", "--stats", nargs="+",
                        default = stats, type = is_stat,
                        help="statistics to compute")
    parser.add_argument("-g", "--group", nargs="+",
                        help="parameters by which to "\
                             "group.  Names should be "\
                             "found in the parameters "\
                             "file.  "
                       )
    parser.add_argument("-d", "--deltas",
                        help="If group is specified, "\
                             "deltas may be used to impose "\
                             "grid boxes on the summary "\
                             "rather than using point "\
                             "values.",
                         nargs="+", type = float
                       )
    parser.add_argument("-o", "--output-directory",
                        default="/gpfs/scratch/mjw5407/"
                                "task1/stats/"
                       )
    return parser.parse_args()

def compute(data, stat):
    if stat == "mean":
        return data.mean()
    if stat == "variance":
        return data.var()
    if is_quantile(stat):
        quantile = float(stat[1:]) / 100.0
        if quantile == 0.0:
            return data.min()
        return data.quantile(quantile)
    if stat == "max" or stat == "q100":
        return data.max()
    if stat == "min":
        return data.min()

def analyze(data, stats, group=None, deltas=None):
    results = []
    if group is None:
        group = ["Set"]
    togroupby = copy.copy(group)
    ii = 0
    if deltas is None:
        togroupby = group
    else:
        while ii < len(group) and ii < len(deltas):
            colname = "grid_{0}".format(group[ii])
            gridnumbers = numpy.floor(data[group[ii]].apply(
                            lambda val: val / deltas[ii]))
            data[colname] = gridnumbers.apply(
                            lambda val: val * deltas[ii])
            togroupby[ii] = colname
            ii += 1
        
    print "analyzing grouped by {0}".format(group)
    gb = data.groupby(togroupby)
    for stat in stats:
        print "computing {0}".format(stat)
        tag = "{0}_{1}".format("_".join(group), stat)
        results.append((tag, compute(gb, stat)))
        
    return results

def write_result(infn, result, outputdir):
    fn = "_".join([result[0], os.path.basename(infn)])
    fn = re.sub("\.hv$", "", fn)
    fn = os.path.join(outputdir, fn)
    print "writing {0}".format(fn)
    result[1].to_csv(fn, sep=" ", index=True)    

def cli():
    args = get_args()
    data = pandas.read_table(args.data, sep=" ")
    parameters = pandas.read_table(
                               args.parameters, sep=" ",
                               names=["name","low","high"],
                               header=None)
    param_names = parameters["name"].values
    parameterizations = pandas.read_table(
                               args.parameterizations,
                               sep=" ",
                               names = param_names,
                               header = None)
    data = data.join(parameterizations, on=["Set"], 
                     how="outer")

    if args.deltas is not None:
        deltas = args.deltas
    else:
        deltas = []

    results = analyze(data, args.stats, args.group, deltas)
    for result in results:
        write_result(args.data.name, result, 
                     args.output_directory)

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
