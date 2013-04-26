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

class InvalidProblemError(Exception): pass

class Job(object):
    """
    Job: generate a reference set from the 50 seeds for
    a particular algo/problem.
    """
    def __init__(self, algo, problem, inputdir, outputdir):
        """
        figure out what epsilons are and what the problem name
        is.  
        """
        self.algo = algo
        self.problem = problem
        self.ndvs, obj_scale = problem.split("_",1)
        self.epsilons = {
            "10_1.0": "0.15,30.0,6.0,0.03,30.0,"\
                      "3000.0,150.0,0.3,3.0,0.3",
            "3_1.0":  "1.0,1.0,1.0",
            "3_0.1":  "0.1,0.1,0.1"
        }[obj_scale]

        self.name = "_".join([algo, problem])
        self.inputdir = os.path.join(
                                inputdir,"_".join([algo,problem]))
        self.outputdir = outputdir
        self.outputfile = os.path.join(self.outputdir, 
                                       "{0}.ref".format(self.name))

    def pbs_script(self):
        """
        Build a PBS script for the job
        """
        classpath = ["./lib/{0}".format(fn) for fn 
                     in os.listdir("lib") 
                     if re.search("\.jar$", fn)
                    ]
        classpath.append(".")
        java_args = "-Xmx1g -server -classpath {0}".format(
            ":".join(classpath))

        inputs = [os.path.join(self.inputdir, fn) 
                  for fn in os.listdir(self.inputdir)
                  if re.search("\.sets$", fn)]
              
        merger = "PSOResultFileMerger"
        merger_args = [
            "--dimension",
            str(len(self.epsilons.split(","))),
            "--epsilon",
            self.epsilons,
            "--vars",
            self.ndvs,
            "--output",
            self.outputfile,
            " ".join(inputs)
            ]

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

    def __repr__(self):
        return self.name

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("algos",
                        help="comma-delimited set of algorithms "\
                             "from among Borg, eMOEA, NSGAII, "\
                             "eNSGAII, GDE3, and BorgRecency"
                        )
    parser.add_argument("problems",
                        help="comma-delimited list of problems "\
                             "from among 27_10_1.0, 27_3_1.0, "\
                             "27_3_0.1, 18_10_1.0, 18_3_1.0, "\
                             "and 18_3_0.1"
                       )
    parser.add_argument("-i", "--inputdir",
                        default="/gpfs/scratch/mjw5407/task1/sets",
                        help="directory where algo_problem "\
                             "subdirectories can be found"
                       )
    parser.add_argument("-o", "--outputdir",
                        default="/gpfs/scratch/mjw5407/task1/ref",
                        help="directory where reference sets "\
                             "are to be accumulated"
                       )
    parser.add_argument("-v", "--verbose",
                        action='store_true')
    args =  parser.parse_args()
    return args

def jobs(algos, problems, inputdir, outputdir):
    thejobs = []
    for algo in algos:
        for problem in problems:
            thejobs.append(Job(algo, problem, inputdir, outputdir))
    return thejobs

def cli():
    args = get_args()
    valid_algos = ["Borg", "eMOEA", "NSGAII", 
                   "eNSGAII", "GDE3", "BorgRecency"]
    valid_problems = ["27_10_1.0", "27_3_1.0", "27_3_0.1", 
                      "18_10_1.0", "18_3_1.0", "18_3_0.1"]
    algos = args.algos.split(",")
    for algo in algos:
        if not algo in valid_algos:
            print "Algorithm {0} not among {1}".format(
                        algo, ", ".join(valid_algos))
            return
    problems = args.problems.split(",")
    for problem in problems:
        if not problem in valid_problems:
            print "Problem {0} not among {1}".format(
                        problem, ", ".join(valid_problems))
            return
    for job in jobs(algos, problems, args.inputdir, args.outputdir):
        pbsid = job.submit()
        print "{0}: {1}".format(pbsid, job)
        if args.verbose:
            print "\n".join(job.pbs_script())
            print ""

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
