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

def epsilon_tag(eps_scaling):
    if abs(eps_scaling - 1.0) < 1e-5:
        return ""
    return re.sub("\.", "_", str(eps_scaling))

class Job(object):
    """
    represents a job that might be submitted
    """
    def __init__(self, algo, dvs, objs, seed, workdir, 
                 eps_scaling=1.0):
        """
        figure out what epsilons are and what the problem name
        is.  
        """
        self.algo = algo
        self.seed = seed
        self.dvs = dvs
        self.objs = objs
        self.eps_scaling = eps_scaling
        default_epsilons = {
            3: (1,1), 
            10: (0.15,30.0,6.0,0.03,30.0,3000.0,150.0,0.3,3.0,0.3)
        }
        self.epsilons = tuple([eps * eps_scaling 
                               for eps in default_epsilons[objs]])
        self.problem = "GAA_{0}_{1}".format(dvs, objs)
        self.name = "_".join([algo, self.problem, str(self.seed)])
        self.epsilon_tag = epsilon_tag(eps_scaling)
        self.workdir = workdir

    def setsfile(self):
        return os.path.join(
            "{0}{1}".format(self.workdir, self.epsilon_tag),
            "{0}.sets".format(self.name)
            )

    def parameterizations_completed(self):
        """
        how many of the parameterizations in the Sobol' sequence 
        have been run
        """
        filename = self.setsfile()
        count = 0
        if not os.path.isfile(filename):
            return 0

        with open(filename, 'rb') as ifp:
            for line in ifp:
                if "EvaluationTime" in line:
                    count += 1

        return count

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
        evaluator = "org.moeaframework.analysis.sensitivity.Evaluator"
        evaluator_args = ""\
            "--parameterFile ./params/{0}_Params "\
            "--input ./params/{0}_Sobol "\
            "--problem {1} "\
            "--algorithm {0} "\
            "--seed {2} "\
            "--output {3} "\
            "-x epsilon={4}".format(
                self.algo,
                self.problem,
                self.seed,
                self.setsfile(),
                ",".join([str(eps) for eps 
                in self.epsilons])
                )

        script = [
            "#PBS -N {0}".format(self.name),
            "#PBS -l nodes=1",
            "#PBS -l walltime=24:00:00",
            "#PBS -o output/{0}{1}".format(
                self.epsilon_tag, self.name),
            "#PBS -e error/{0}{1}".format(
                self.epsilon_tag, self.name),
            "cd $PBS_O_WORKDIR",
            "java {0} {1} {2}".format(
                java_args, evaluator, evaluator_args)
            ]
                       
        return script

    def is_submitted(self, statuses):
        """
        Return the Job ID of the job, or None
        """
        filename = "output/{0}{1}$".format(
                       self.epsilon_tag, self.name)
        matches = [status for status in statuses 
                   if re.search(filename, status["Output_Path"])
                  ]
        if len(matches) > 0:
            return matches[0]["Job_Id"]
        return None

    def submit(self):
        script = self.pbs_script()
        child = Popen("qsub", stdin=PIPE, stdout=PIPE)
        child.stdin.write("\n".join(script))
        child.stdin.close()
        jobid = child.stdout.read()
        sys.stdout.flush()
        return jobid

    def __repr__(self):
        return "{0} {1} {2} {3} {4}".format(
                self.algo, self.dvs, self.objs, self.seed,
                self.eps_scaling)

    def get_status_row(self, df):
        return df[
            (df["alg"]   ==    self.algo        ) &\
            (df["dv"]    ==    self.dvs         ) &\
            (df["obj"]   ==    self.objs        ) &\
            (df["seed"]  ==    self.seed        ) &\
            (df["eps"]   ==    self.eps_scaling ) 
            ]
        

def qstat_u(user):
    """
    get job ids owned by user
    """
    child = Popen(["qstat", "-u{0}".format(user)], stdout=PIPE)
    # first 5 lines are header info. munch them
    for _ in range(5):
        child.stdout.readline()
    pbs_ids = [line.split(".")[0] for line in child.stdout]
    return pbs_ids

def qstat_f_x(pbs_id):
    """
    get certain status info from full-job query
    """
    child = Popen(["qstat", "-f", "-x", str(pbs_id)], stdout=PIPE)
    result = child.stdout.read()
    exemel = ET.fromstring(result)
    status = {}
    for tag in ("Job_Name", "job_state", "Job_Id",
                "Error_Path", "Output_Path"):
        for xx in exemel.iter(tag): #there's only one of each tag
            status[tag] = xx.text

    return status


def get_args():
    parser = argparse.ArgumentParser()
    args =  parser.parse_args()
    return args

def cli():

def jobs(args):
    """ 
    Create a job for every job specified on the command line
    """
    return jobs


if __name__ == "__main__":
    cli()
    args = cli()
    thejobs = jobs(args)
    st = status(thejobs, args.statusfile)
    counter = 0
    for job in thejobs:
        statusrow = job.get_status_row(st)
        if statusrow["sets"] < statusrow["needed"]:
            pbsid = statusrow["PBSid"]
            if pbsid.isnull():
                pbsid = job.submit()
                statusrow["PBSid"] = pbsid
                print "submitted", pbsid, repr(job)
                time.sleep(0.1)
        counter += 1
        if counter % 20 == 0:
            st.to_csv(args.statusfile, sep="\t")
    st.to_csv(args.statusfile, sep="\t")

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
