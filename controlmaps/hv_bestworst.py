"""
hvbestworst

Load up all the stats files for problems matching a pattern
and find the worst and best metric values therein
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
