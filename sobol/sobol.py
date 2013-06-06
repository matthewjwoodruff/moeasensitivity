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

sobol.py
"""

from subprocess import Popen, PIPE
import os
import re
import argparse
import time

def classpath():
    cp = ["./lib/{0}".format(fn) for fn in os.listdir("lib") 
                 if re.search("\.jar$", fn) ]
    cp.append(".")
    return cp

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("algo", 
                        help="Algorithm on which to do Sobol'"\
                             "analysis.")
    parser.add_argument("problem",
                        help="Problem on which to do Sobol'"\
                             "analysis.")
    parser.add_argument("-d", "--stats-directory",
                        help="directory in which to find "\
                             "statistical summaries by set.",
                        default="/gpfs/scratch/mjw5407/task1/stats/")
    parser.add_argument("-o", "--output-directory",
                        default="/gpfs/scratch/mjw5407/task1/sobol"\
                                "/temp",
                        help="directory in which to place "\
                             "results.")
    parser.add_argument("-s", "--statistic",
                        default = "mean",
                        help = "which statistic to analyze")
    parser.add_argument("-m", "--metric",
                        default = "Hypervolume",
                        help = "which metric to analyze")
    parser.add_argument("-r", "--resamples", type=int,
                        help = "number of bootstrap resamples",
                        default = 1000)

    return parser.parse_args()

def commandline(algo, problem, inputfile, column, resamples):
    cml = ["java", "-Xmx1g", "-server", "-classpath",
           ":".join(classpath())]
    cml.append(".".join(
              ["org","moeaframework","analysis","sensitivity",
               "SobolAnalysis"]))
    sobol_args = ["--parameterFile",
                  "params/{0}_Params".format(algo),
                  "--input", inputfile,
                  "--metric", str(column),
                  "--resamples", str(resamples)]

    cml.extend(sobol_args)

    return cml

def strip(origin, destination):
    """
    all we're doing is calling tail -n +2 because 
    MOEAFramework is header-intolerant
    """
    with open(destination, 'w') as ofp:
        child = Popen(["tail", "-n", "+2", origin], stdout = ofp)
        child.wait()

class NoMetricError(Exception): pass

def column_number(column_name, filename):
    with open(filename, 'r') as fp:
        header = fp.readline()
        row = header.strip().split(" ")
    try:
        return row.index(column_name)
    except ValueError:
        raise NoMetricError("No metric {0} in {1}".format(
                column_name, filename))

def sobol(algo, problem, stats_directory, 
                temp_directory, stat, metric, resamples):
    fn = "Set_{2}_{0}_{1}".format( algo, problem, stat)
    origin = os.path.join(stats_directory, fn)
    column = column_number(metric, origin)

    tempset = os.path.join(temp_directory, fn)
    strip(origin, tempset)

    cml = commandline(algo, problem, tempset, column, resamples)
    fn = os.path.join(temp_directory, 
                      "report_{0}_{1}_{2}_{3}".format(
                            algo, problem, stat, metric))
    with open(fn, 'w') as report:
        child = Popen(cml, stdout = report)
        child.wait()

    os.unlink(tempset)
    
def cli():
    args = get_args()
    sobol(args.algo, args.problem, args.stats_directory, 
                     args.output_directory,
                     args.statistic, args.metric,
                     args.resamples)

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
