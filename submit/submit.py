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

===========================================================
submit.py
check status of running jobs and output files, decide what jobs
to start
"""

from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import os
import re
import sys
import argparse
import pandas
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
            3: (1,1,1), 
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
        
def valid_problem(problem):
    """
    true if the problem is one of the ones supported
    by Dave in MOEAFramework
    """
    valid_problems = ["GAA_{0}_{1}".format(dvs, objs) 
                      for dvs in (18, 27)
                      for objs in (3, 10)]
    return problem in valid_problems

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

def parameterizations_required(algorithm):
    number_required = {"Borg":    10032,
                       "eMOEA":   10010,
                       "eNSGAII": 10010,
                       "GDE3":    10000,
                       "MOEAD":   10000,
                       "NSGAII":  10010
                       }
    return number_required[algorithm]

def oldsubmit(workdir, algos, problems, seeds, eps_scaling = 1.0):
    statuses = [qstat_f_x(pbs_id) for pbs_id in qstat_u("mjw5407")]
    target_directory = "{0}{1}".format(workdir, epsilon_tag(eps_scaling))
    if not os.path.exists(target_directory):
        os.mkdirs(target_directory)

    for dvs, objs in problems:
        for seed in seeds:
            for algo in algos:
                job = Job(algo, dvs, objs, seed, workdir, eps_scaling)
                if not valid_problem(job.problem):
                    raise InvalidProblemError(job.name)
                jobid = job.is_submitted(statuses)
                if jobid:
                    print "{0} {1} already submitted as {2}".format(
                        job.name, eps_scaling, jobid)
                    continue
                completed = job.parameterizations_completed(workdir)
                required = parameterizations_required(algo)
                if required <= completed: 
                    print "{0} {1} is complete".format(
                              job.name, eps_scaling)
                    continue
                job.submit(workdir)

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--statusfile", 
                        help="Status file in the format produced by"
                             "info.sh",
                        default = "status.txt"
                       )
    parser.add_argument("-a", "--algos",
                        help="Comma-separated list of algorithms to"
                             "use",
                        default="Borg,eMOEA,NSGAII,eNSGAII,GDE3"
                       )
    parser.add_argument("-p", "--problems",
                        help="Comma-separated list of problems to"
                             "submit",
                        default="27_10,18_10,27_3_0.1,18_3_0.1"
                       )
    parser.add_argument("-s", "--seeds",
                        help="Comma-separated begin/end pair of "
                             "seeds to submit",
                        default="1,50"
                       )
    parser.add_argument("-w", "--workdir",
                        help="working directory",
                        default="./sets"
                       )
    args =  parser.parse_args()
    return args

def jobs(args):
    """ 
    Create a job for every job specified on the command line
    """
    problems = [problem for problem in args.problems.split(",")]
    for ii in range(len(problems)):
        problem = problems[ii].split("_")
        dv = int(problem[0])
        obj = int(problem[1])
        if len(problem) > 2:
            eps = float(problem[2])
        else:
            eps = 1.0
        problems[ii] = (dv, obj, eps)

    seeds = [int(seed) for seed in args.seeds.split(",")]
    seeds = range(seeds[0], seeds[1] + 1)
    workdir = args.workdir

    jobs = []
    for algo in args.algos.split(","):
        for dv, obj, eps in problems:
            for seed in seeds:
                jobs.append(Job(algo, dv, obj, seed, workdir, eps))

    return jobs

def status(thejobs, statusfile):
    """
    Returns jobs' status based on status file.
    If status file can't be read, then falls back on
    scanning the working directory
    """
    qstatuses = [qstat_f_x(pbs_id) for pbs_id in qstat_u("mjw5407")]
    if statusfile:
        try:
            with open(statusfile,'r') as status:
                pass
        except IOError:
            statusfile = None

    if statusfile:
        df = pandas.read_table(statusfile, index_col=0, header=0)
    else:        
        df = pandas.DataFrame(
                columns=["time", "path", "alg", "dv", "obj", "seed", 
                         "eps", "sets", "needed", "PBSid"]
                )
    table = []
    for job in thejobs:
        statusrow = job.get_status_row(df)
        setsfile = job.setsfile()
        try:
            with open(setsfile, 'r') as thesetsfile:
                stat = os.stat(setsfile)
                timestring = time.strftime("%Y-%m-%d %H:%M:%S",
                                       time.gmtime(stat.st_mtime))
        except IOError:
            timestring = ""
        # if currently executing job, don't bother updating
        pbsid = job.is_submitted(qstatuses)
        uptodate = False
        if len(statusrow) > 0:
            uptodate = statusrow.irow(0)["time"] == timestring
            if uptodate: print setsfile, "is up to date"
            
        if uptodate: # implies len(statusrow) > 0
            statusrow["PBSid"]=pbsid
            statusrow = list(statusrow.irow(0))
        else:
            if pbsid and (len(statusrow) > 0):
                print "not scanning {0}, job exists".format(
                    setsfile)
                statusrow["PBSid"] = pbsid
                statusrow = list(statusrow.irow(0))
            else:
                print "scanning {0}...".format(setsfile),
                sys.stdout.flush()
                completed = job.parameterizations_completed()
                print completed
                statusrow = [timestring, setsfile, job.algo, 
                             job.dvs, job.objs, job.seed, 
                             job.eps_scaling, completed, 
                             parameterizations_required(job.algo),
                             job.is_submitted(qstatuses)
                            ]
        table.append(statusrow)
                      

    # careful! this blows away the state!
    df = pandas.DataFrame(
        columns=["time", "path", "alg", "dv", "obj", "seed", 
                 "eps", "sets", "needed", "PBSid"],
        data = table
        )
            
    return df

if __name__ == "__main__":
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
