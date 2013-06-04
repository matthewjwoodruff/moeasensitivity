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

broaden_refset.py
Take a file summarizing utopia and nadir points for each problem,
along with the reference set for each set of objectives, and use 
them to generate an expanded reference set that will force the
hypervolume calculation to use a reasonable nadir point.
"""
import argparse
import os
import copy

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("unfile", type=argparse.FileType("r"),
                        help="file produced by scanproblem.py")
    parser.add_argument("objectives", help="10_1.0, 3_0.1, etc.")
    parser.add_argument("-r", "--refdir", 
                        help="directory with reference sets in it",
                        default = "/gpfs/scratch/mjw5407/task1/ref")
    parser.add_argument("-o", "--output-dir",
                        help="where to write expanded reference"\
                             "sets",
                        default = ".")
    return parser.parse_args()
    
def read_refset(refdir, objectives):
    fn = os.path.join(refdir, "m.{0}.ref".format(objectives))
    rows = []
    with open(fn, "r") as fp:
        line = fp.readline()
        while line != '':
            row = line.strip().split(" ")
            row = [float(text) for text in row]
            rows.append(row)
            line = fp.readline()
    return rows

def read_unfile(unfile):
    line = unfile.readline()
    header = line
    line = unfile.readline()
    rows = []
    while line != '':
        row = line.strip().split(" ")
        rows.append(row)
        line = unfile.readline()
    return rows

def axial_points(objectives, undata):
    utopia, nadir = (None, None)
    for row in undata:
        if objectives in row[0]: 
            _, ut, na= row
            ut = [float(text) for text in ut.split(",")]
            na = [float(text) for text in na.split(",")]
            if utopia is None:
                utopia = ut
                nadir = na
            else:
                utopia = [min(cur, best) for cur, best 
                          in zip(ut, utopia)]
                nadir = [max(cur, worst) for cur, worst 
                          in zip(na, nadir)]
    axial = []
    for ii in range(len(utopia)):
        point = copy.copy(utopia)
        point[ii] = nadir[ii]
        axial.append(point)
    return axial
    
def write_refset(data, filename):
    with open(filename, "w") as fp:
        for row in data:
            fp.write(" ".join([str(val) for val in row]))
            fp.write("\n")
        fp.write("#\n")

def cli():
    args = get_args()
    undata = read_unfile(args.unfile)
    axial = axial_points(args.objectives, undata)
    refset = read_refset(args.refdir, args.objectives)
    refset.extend(axial)
    write_refset(refset,
                 os.path.join(
                    args.output_dir, 
                    "m.{0}_extended.ref".format(args.objectives)))

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
