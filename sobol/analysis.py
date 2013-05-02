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

analysis.py

Run sobol' analysis and tabulate the results
"""

import argparse
import itertools
from tabulate import tabulate
from sobol import sobol

def get_args():
    description = "Run Sobol' analysis and tabulate the results."\
                  "Depends on file naming conventions from "\
                  "stats.py"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("algorithms",
                        help="comma-separated list of MOEAs")
    parser.add_argument("problems",
                        help="comma-separated list of problems, "\
                             "e.g. 27_10_1.0")
    parser.add_argument("output_file",
                        type = argparse.FileType("w"),
                        help="file in which to write "\
                             "tabulated results")
    parser.add_argument("-s", "--stats", 
                        default = "mean,q10,q50,q90",
                        help = "comma-separated list of stats, "\
                               "default is mean,q10,q50,q90")
    parser.add_argument("-m", "--metrics", default = "Hypervolume",
                        help = "comma-separated list of metrics, "\
                               "default is Hypervolume")
    parser.add_argument("-d", "--stats-directory",
                        default="/gpfs/scratch/mjw5407/task1/stats",
                        help="directory where statistics files "\
                             "are found")

    parser.add_argument("-t", "--temp-directory", 
                        default="/gpfs/scratch/mjw5407/task1/"\
                                "sobol/temp",
                        help="directory in which to place "\
                             "intermediate results.")
    return parser.parse_args()

def analysis(algos, problems, stats, metrics, statsdir,
                tempdir, outfile):
    for algo, problem, stat, metric in itertools.product(
            algos, problems, stats, metrics):
        sobol(algo, problem, statsdir, tempdir, stat, metric)

    tabulate(algos, problems, stats, metrics, tempdir, outfile)

def cli():
    args = get_args()
    algos = args.algorithms.split(",")
    problems = args.problems.split(",")
    stats = args.stats.split(",")
    metrics = args.metrics.split(",")

    analysis(algos, problems, stats, metrics, args.stats_directory,
                args.temp_directory, args.output_file)

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
