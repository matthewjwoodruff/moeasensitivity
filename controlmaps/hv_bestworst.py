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
hvbestworst

Load up all the stats files for problems matching a pattern
and find the worst and best metric values therein.

Can use this with best=, worst= in controlmaps.py to scale
differently.  Say for example you wanted to scale everything
by the tenth and ninetieth quantile values.  You could do that.
"""
import os
import glob
import argparse
import pandas

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem", 
                        help = "pattern to match for the problem")
    parser.add_argument("-d", "--stats-dir",
                      default = "/gpfs/scratch/mjw5407/task1/stats",
                      help = "directory where metrics files are")
    parser.add_argument("-s", "--stat", default = "*",
                        help = "which stat to use")

    return parser.parse_args()

def scan(stat,problem, dirname):
    globby = "*_{0}_*{1}*".format(stat,problem)
    print globby
    filenames = glob.glob(os.path.join( dirname,  globby))
                            
    print filenames
    worst = 1.0
    best = 0.0

    for fn in filenames:
        if "variance" in fn:
            print "skipping {0}".format(fn)
            continue
        if "Set" in fn:
            print "skipping {0}".format(fn)
            continue
        print "scanning {0}".format(fn)
        metrics = pandas.read_table(fn, sep=" ")
        worst = min(metrics["Hypervolume"].min(), worst)
        best = max(metrics["Hypervolume"].max(), best)
        print (worst, best)

    return worst, best

def cli():
    args = get_args()
    print scan(args.stat, args.problem, args.stats_dir)

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
