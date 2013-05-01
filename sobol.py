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

submit.py
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
    parser.add_argument("-s", "--sets-directory",
                        help="directory in which to find "\
                             "statistical summaries by set.",
                        default="/gpfs/scratch/mjw5407/task1/stats/")
    parser.add_argument("-o", "--output-directory",
                        default="/gpfs/scratch/mjw5407/task1/sobol",
                        help="directory in which to place "\
                             "results.")
    parser.add_argument("-t", "--temp-directory",
                        default="/gpfs/scratch/mjw5407/task1/"\
                                "sobol/temp",
                        help="directory in which to place "\
                             "results.")
    return parser.get_args()

def commandline(algo, problem, statsdir):
    cml = ["java", "-Xmx1g", "-server", "-classpath",
           ":".join(classpath())]
    cml.append(".".join(
              ["org","moeaframework","analysis","sensitivity",
               "SobolAnalysis"]))
    sobol_args = ["--parameterFile",
                  "params/{0}_Params".format(algo),
                  "--input",
                  os.path.join(setsdir, "Set_mean_{0}_{1}".format(
                    algo, problem)),
                  "--metric", "2"]

    cml.extend(sobol_args)

    return cml



def cli():
    args = get_args()

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
