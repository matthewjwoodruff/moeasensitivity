"""
Hypervolume.
I have 6 problem instances, times 6 algorithms, times 50
seeds per algorithm.  That's 1800 sets files.  I do not
want 1800 10000 row hypervolume files.  I want 36 
500000 row hypervolume files.
So do all seeds by default.
Seed is always the last thing before .sets.
"""
from subprocess import Popen, PIPE
import re
import glob
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("algo",
                        help="algorithm to analyze")
    parser.add_argument("ndv", choices = [18, 27],
                        type=int,
                        help="number of decision variables")
    parser.add_argument("nobj", choices = [10, 3],
                        type=int,
                        help="number of objectives")
    parser.add_argument("eps", choices = [1.0, 0.1],
                        type=float,
                        help="epsilon scale")
    parser.add_argument("-r", "--referencefile",
                        help="file containing reference "\
                             "set.  Defaults to /gpfs/"\
                             "scratch/mjw5407/task1/ref/"\
                             "m.{NOBJ}_{EPS}.ref"
                       )
    parser.add_argument("-s", "--setsdirectory",
                        help="directory where solution "\
                             "sets are stored.  Defaults "\
                             "to /gpfs/scratch/mjw5407/"\
                             "task1/sets/{ALGO}_{NDV}_"\
                             "{NOBJ}_{EPS}"
                       )
    parser.add_argument("-o", "--outputfile",
                        type=argparse.FileType("w"),
                        help="file where hypervolume "\
                             "results are stored"\
                             "Defaults to /gpfs/scratch/"\
                             "mjw5407/task1/hv/{ALGO}_"\
                             "{NDV}_{NOBJ}_{EPS}.hv"
                       )
    parser.add_argument("-w", "--workingdirectory",
                        help="directory where temporary "\
                             "working files will be placed"\
                             "Defaults to /gpfs/scratch/"\
                             "mjw5407/task1/hv/temp"
                       )

    return parser.parse_args()

def outputfile(algo, ndv, nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/hv/"\
           "{0}_{1}_{2}_{3}.hv".format(algo, ndv, nobj, eps)

def referencefilename(nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/ref/"\
           "m.{0}_{1}.ref".format(nobj, eps)

def setsdirectory(algo, ndv, nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/sets/"\
           "{0}_{1}_{2}_{3}".format(algo, ndv, nobj, eps)

def workingdirectory():
    return "/gpfs/scratch/mjw5407/task1/hv/temp"

def awkscript(ndv, nobj, otpt):
    percents = ["%s"]*nobj
    dollars = ["${0}".format(ndv+ii+1) for ii in range(nobj)]
    script = ";".join(['BEGIN {{FS=" "}}',
             '/^#/ {{print $0 > "{0}"}}',
             '/^[0-9]/ {{printf "{1}\\n",{2}  > "{0}"}}'])
    return script.format(otpt, " ".join(percents), 
                               ",".join(dollars))

def strip_dvs(ndv, nobj, setsfile, tempfile):
    awktext = awkscript(ndv, nobj, tempfile)
    cml = ["awk", awktext, setsfile]
    print " ".join(cml)
    child = Popen(cml)
    child.wait()

def classpath():
    cp = ["./lib/{0}".format(fn) for fn in os.listdir("lib") 
                 if re.search("\.jar$", fn) ]
    cp.append(".")
    return cp

def temp_input_filename(workdir, setsfile):
    fn = "reduced_{0}".format(os.path.basename(setsfile))
    return os.path.join(workdir, fn)

def temp_output_filename(workdir, setsfile):
    fn = "hyper_{0}".format(os.path.basename(setsfile))
    return os.path.join(workdir, fn)


def commandline(nobj, ref, tempin, tempout):
    cml = ["java", "-Xmx1g", "-server", "-classpath",
           ":".join(classpath())]
    cml.append(
           ".".join(["org", "moeaframework", "analysis", 
                     "sensitivity", "ResultFileEvaluator"]))
    cml.extend([
            "--dimension", str(nobj),
            "--output", tempout,
            "--input", tempin,
            "--reference", ref
            ])
    return cml

def write_seed(outfp, infp, seed):
    line = infp.readline()
    while line:
        outfp.write("{0} {1}".format(seed, line))
        line = infp.readline()

def evaluate_sets(ref, sets, outfp, workdir, ndv, nobj):
    for aset in sets:
        tempin = temp_input_filename(workdir, aset)
        tempout = temp_output_filename(workdir, aset)
        if os.path.exists(tempout):
            print "already done, skipping {0}".format(aset)
            continue
        strip_dvs(ndv, nobj, aset, tempin)
        cml = commandline(nobj, ref, tempin, tempout)
        print " ".join(cml)
        child = Popen(cml)
        child.wait()
        seed = aset.split("_")[-1]
        seed = seed.split(".")[0]
        with open(tempout, "r") as infp:
            write_seed(outfp, infp, seed)
        #os.unlink(tempin)
        #os.unlink(tempout)

def cli():
    args = get_args()
    if args.referencefile:
        ref = args.referencefile
    else:
        ref = referencefilename(args.nobj, args.eps)
    if args.setsdirectory:
        setsdir = args.setsdirectory
    else:
        setsdir = setsdirectory(args.algo, args.ndv, 
                                args.nobj, args.eps)
    sets = glob.glob(os.path.join(setsdir, "*sets"))

    if args.workingdirectory:
        workdir = args.workingdirectory
    else:
        workdir = workingdirectory()

    if args.outputfile:
        outfp = args.outputfile
    else:
        outfp = open(outputfile(args.algo, args.ndv, 
                                args.nobj, args.eps), "w")

    evaluate_sets(ref, sets, outfp, workdir,
                    args.ndv, args.nobj)
    ref.close()
    outfp.close()

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
