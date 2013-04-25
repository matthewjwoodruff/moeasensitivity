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

scanproblem.py
Scan all result sets for a problem to produce utopia and nadir
points based on those sets.

"""
import bestandworst
import argparse
import glob
import os
import sys

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem", 
                        help = "27_10_1.0, 18_3_0.1, et cetera")
    dirname = "/gpfs/scratch/mjw5407/task1/sets/"
    parser.add_argument("-s", "--sets-directory",
                        help = "defaults to {0}".format(dirname),
                        default = dirname)
    parser.add_argument("-o", "--output",
                        help = "defaults to stdout",
                        type = argparse.FileType("a"),
                        default = sys.stdout)
    return parser.parse_args()
                        
def scan_problem(problem, dirname):
    ndvs, nobjs, _ = problem.split("_")
    ndvs = int(ndvs)
    nobjs = int(nobjs)
    first = ndvs
    last = ndvs + nobjs - 1
    setsdirs = glob.glob(os.path.join(dirname, 
                                       "*{0}".format(problem)))
    globalbest = None
    globalworst = None
    for setsdir in setsdirs:
        setsfiles = glob.glob(os.path.join(setsdir, "*sets"))
        for setsfile in setsfiles:
            sys.stderr.write(setsfile)
            sys.stderr.write("\n")
            with open(setsfile, "r") as fp:
                best, worst = bestandworst.scan(fp, first, last)
            sys.stderr.write("{0}".format(best))
            sys.stderr.write("\n")
            sys.stderr.write("{0}".format(worst))
            sys.stderr.write("\n")

            if globalbest is None:
                globalbest = best
                globalworst = worst
            else:
                globalbest = [min(a,b) for a, b 
                              in zip(best, globalbest)]
                globalworst = [max(a,b) for a, b 
                               in zip(worst, globalworst)]
    return globalbest, globalworst
    
def cli():
    args = get_args()
    best, worst = scan_problem(args.problem, args.sets_directory)
    args.output.write(args.problem)
    args.output.write(" ")
    args.output.write(",".join([str(val) for val in best]))
    args.output.write(" ")
    args.output.write(",".join([str(val) for val in worst]))
    args.output.write("\n")

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
