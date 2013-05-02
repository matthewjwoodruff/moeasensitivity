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

tabulate.py

Tabulate Sobol' sensitivity indices from the MOEAFramework Sobol'
reports.
"""

import itertools
import re
import argparse
import sys
import os

def get_args():
    description = "Tabulate MOEAFramework Sobol' analysis reports "\
                  "into a single data file.  Depends on the naming "\
                  "scheme for reports files used by sobol.py."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("algorithms",
                        help="comma-separated list of algorithms"\
                             "to consolidate")
    parser.add_argument("problems",
                        help="comma-separated list of problems to "\
                             "consolidate")
    parser.add_argument("-s", "--stats", default="mean",
                        help="comma-separated list of stats to "\
                             "consolidate.  (This is in case your "\
                             "Sobol' analysis includes stats "\
                             "other than the mean")
    parser.add_argument("-m", "--metrics", default="Hypervolume",
                        help="comma-separated list of metrics to "\
                             "consolidate.  (In case your Sobol'"\
                             "analysis includes metrics other than"\
                             "Hypervolume.)")
    parser.add_argument("-r", "--reports-directory",
                        help="directory where Sobol' reports "\
                             "produced by sobol.py are stored",
                        default="/gpfs/scratch/mjw5407/task1/sobol"\
                                "/temp")
    parser.add_argument("-t", "--output-table",
                        type = argparse.FileType("w"),
                        help = "where to write the output.  "\
                               "Default: stdout",
                        default = sys.stdout)

    return parser.parse_args()

def tabulate_report(report):
    """
    in: file opened for reading
    out: rows
    """
    orders = ["First-Order Effects", "Total-Order Effects", 
              "Second-Order Effects", ]

    rex = re.compile(
        '(^  ([a-zA-Z0-9.]+)( \* [a-zA-Z0-9.]+)?) '
        +'(-?[0-9]+\.[0-9]+(E[-][0-9]+)?) \[(.*)\]')

    rows = []
    line = report.readline()

    while line:
        line = report.readline()
        if line.strip() in orders:
            order = line.split("-")[0] 

        matches = re.search(rex, line)
        if matches:
            # groups: (0) is the name of the input
            groups = matches.groups()
            inputname = groups[1].strip()
            if groups[2]:
                interaction = groups[2].strip()[2:]
            else:
                interaction = ""
            sensitivity = groups[3].strip()
            confidence = groups[5].strip()
            rows.append([inputname, interaction,
                         order, sensitivity, confidence])
    return rows

def write_table(table, header, data):
    """
    in: file opened for writing, header, data
    out: nothing
    side effect: write header and data to file
    """
    table.write(" ".join(header))
    table.write("\n")
    table.write("\n".join([" ".join(row) for row in data]))
    table.write("\n")

def cli():
    args = get_args()
    algos = args.algorithms.split(",")
    problems = args.problems.split(",")
    stats = args.stats.split(",")
    metrics = args.metrics.split(",")

    rows = []
    for algo, problem, stat, metric in itertools.product(
            algos, problems, stats, metrics):
        reportname = "report_{0}_{1}_{2}_{3}".format(
                        algo, problem, stat, metric)
        fn = os.path.join(args.reports_directory, reportname)
        with open(fn, 'r') as report:
            reportrows = tabulate_report(report)
            identity = [algo, problem, stat, metric]
            rows.extend([identity + row for row in reportrows])
    header = ["algo", "problem", "stat", "metric", "input", 
              "interaction", "order", "sensitivity", "confidence"]
    write_table(args.output_table, header, rows)

if __name__ == "__main__":
    cli()
# vim:sw=4:ts=4:expandtab:fdm=indent:colorcolumn=68:ai
