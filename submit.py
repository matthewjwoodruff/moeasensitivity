"""
check status of running jobs and output files, decide what jobs
to start
"""

from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import os
import re
import sys
import argparse
import time
from collections import namedtuple


"""
        script = [
            "#PBS -N {0}".format(self.name),
            "#PBS -l nodes=1:ppn=1",
            "#PBS -l walltime=24:00:00",
            "#PBS -o {0}".format(os.path.join("output",self.name)),
            "#PBS -e {0}".format(os.path.join("error",self.name)),
            "cd $PBS_O_WORKDIR",
            "java {0} {1} {2}".format(
                java_args, merger, " ".join(merger_args))
            ]
                       
        return script

    def submit(self):
        script = self.pbs_script()
        child = Popen("qsub", stdin=PIPE, stdout=PIPE)
        child.stdin.write("\n".join(script))
        child.stdin.close()
        jobid = child.stdout.read()
        sys.stdout.flush()
        return jobid.strip()
"""

def commandline(algo, ndv, nobj, eps):
    return ["python", "compute_hypervolumes.py", 
            algo, ndv, nobj, eps]

def script(commandline, name):
    script = [
                "#PBS -N {0}".format(name),
                "#PBS -l nodes=1:ppn=1",
                "#PBS -l walltime=24:00:00",
                "#PBS -o {0}".format(os.path.join("output",name)),
                "#PBS -e {0}".format(os.path.join("error",name)),
                "cd $PBS_O_WORKDIR",
                " ".join(commandline)
             ]
    return script

def submit(algo, problem):
    ndv, nobj, eps = problem.split("_")
    cml = commandline(algo, ndv, nobj, eps)
    name = "_".join(["hv", problem, algo])
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
    return parser.parse_args()

def cli():
    args = get_args()
    valid_algos = ["BorgRecency", "Borg", "GDE3", 
                   "NSGAII", "eNSGAII", "eMOEA"]
    valid_problems = ["27_10_1.0", "27_3_1.0", "27_3_0.1", 
                      "18_10_1.0", "18_3_1.0", "18_3_0.1"]
    for algo in args.algos.split(","):
        if not algo in valid_algos:
            print "{0}: unknown MOEA".format(algo)
            continue
        for problem in args.problems.split(","):
            if not problem in valid_problems:
                print "{0}: unknown problem".format(problem)
            print submit(algo, problem), algo, problem
            time.sleep(0.5)

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
