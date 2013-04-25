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
Submit a batch of compute_hypervolumes runs to a PBS batch server.
"""

from subprocess import Popen, PIPE
import os
import re
import argparse
import time

def commandline(algo, ndv, nobj, eps, ref, seed):
    cml = ["python", "compute_hypervolumes.py", 
            algo, ndv, nobj, eps, "-r", ref]
    cml.extend(["-s", str(seed)])
    return cml

def script(commandline, name):
    script = [
                "#PBS -N {0}".format(name),
                "#PBS -l nodes=1:ppn=1",
                "#PBS -l walltime=6:00:00",
                "#PBS -o {0}".format(os.path.join("output",name)),
                "#PBS -e {0}".format(os.path.join("error",name)),
                "cd $PBS_O_WORKDIR",
                " ".join(commandline)
             ]
    return script

def submit(algo, problem, refdir, seed=None):
    ndv, nobj, eps = problem.split("_")
    ref = os.path.join(refdir, 
                       "m.{0}_{1}_extended.ref".format(nobj, eps))
    cml = commandline(algo, ndv, nobj, eps, ref, seed)
    name = ["h"]
    if seed is not None:
        name.append(str(seed))
    name.extend([ problem, algo])
    name = "_".join(name)
    child = Popen("qsub", stdin=PIPE, stdout=PIPE)
    child.stdin.write("\n".join(script(cml, name)))
    child.stdin.close()
    jobid = child.stdout.read()
    return jobid.strip()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algos",
                        help="comma-separated list of algorithms",
                        default= "BorgRecency,Borg,GDE3,NSGAII,"\
                                 "eNSGAII,eMOEA")
    parser.add_argument("-p", "--problems",
                        help="comma-separated list of problems",
                        default= "27_10_1.0,27_3_1.0,27_3_0.1,"\
                                 "18_10_1.0,18_3_1.0,18_3_0.1")
    parser.add_argument("-s", "--start-seed", type = int,
                        help="Specify only if you want single-seed "\
                             "runs. These don't accumulate results.",
                        required = True
                       )
    parser.add_argument("-e", "--end-seed", type=int,
                        help="Specify only if you want single-seed "\
                             "runs. These don't accumulate results."
                       )
    parser.add_argument("-r", "--reference-dir", 
                        help="directory with reference files",
                        default="/gpfs/scratch/mjw5407/task1/"\
                                "ref/extended")

    return parser.parse_args()

def cli():
    args = get_args()
        
    valid_algos = ["BorgRecency", "Borg", "GDE3", 
                   "NSGAII", "eNSGAII", "eMOEA"]
    valid_problems = ["27_10_1.0", "27_3_1.0", "27_3_0.1", 
                      "18_10_1.0", "18_3_1.0", "18_3_0.1"]
    refdir = args.reference_dir
    for algo in args.algos.split(","):
        if not algo in valid_algos:
            print "{0}: unknown MOEA".format(algo)
            continue
        for problem in args.problems.split(","):
            if not problem in valid_problems:
                print "{0}: unknown problem".format(problem)
            if args.start_seed is not None and args.end_seed is not None:
                for seed in range(args.start_seed, args.end_seed + 1):
                    print submit(algo, problem, refdir, seed)
                    time.sleep(0.5)
            else:
                print submit(algo, problem, refdir, args.start_seed)
                time.sleep(0.5)

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
