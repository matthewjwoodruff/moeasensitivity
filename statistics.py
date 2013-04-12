"""
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
    parser.add_argument("-s", "--stats", nargs="+",
                        default=["mean", "variance",
                                 "q10", "q50", "q90"],
                        help="statistics to compute")
    parser.add_argument("-g", "--group", nargs="+",
                        action="append",
                        help="parameters by which to "\
                             "group.  Names should be "\
                             "found in the parameters "\
                             "file.  Option may be speci"\
                             "fied more than once."
                       )
    return parser.parse_args()
                        
def cli():
    args = get_args()
    print args

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
