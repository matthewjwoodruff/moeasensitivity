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
from emptysets import find_empty_sets

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
                             "mjw5407/task1/hv/temp/{ALGO}"\
                             "_{NDV}_{NOBJ}_{EPS}/"
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

def workingdirectory(algo, ndv, nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/hv/temp/"\
           "{0}_{1}_{2}_{3}".format(algo, ndv, nobj, eps)


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

def write_seed(outfp, infp, seed, empty_sets):
    header = infp.readline()
    line = infp.readline()
    counter = 0
    emptymetrics = "0.0 Inf Inf 0.0 Inf Inf"
    while line:
        while counter in empty_sets:
            outfp.write("{0} {1} {2}\n".format(
                        seed, counter, emptymetrics)
            counter += 1

        outfp.write("{0} {1} {2}".format(
                   seed, counter, line))
        counter += 1
        line = infp.readline()
        

def evaluate_sets(ref, sets, outfp, workdir, ndv, nobj):
    outfp.write("Seed Set "\
                "Hypervolume GenerationalDistance "\
                "InvertedGenerationalDistance Spacing "\
                "EpsilonIndicator MaximumParetoFrontError\n"
               )
    temp_inputs = []
    temp_outputs = []

    for aset in sets:
        tempin = temp_input_filename(workdir, aset)
        tempout = temp_output_filename(workdir, aset)
        temp_inputs.append(tempin)
        temp_outputs.append(tempout)
        if os.path.exists(tempin):
            print "{0} already exists, skipping awk".format(
                   tempin)
        else:
            strip_dvs(ndv, nobj, aset, tempin)

        cml = commandline(nobj, ref, tempin, tempout)
        print " ".join(cml)
        child = Popen(cml)
        with open(tempin, 'r') as ifp:
            empty_sets, _ = find_empty_sets(ifp)
        child.wait()
        seed = aset.split("_")[-1]
        seed = seed.split(".")[0]
        with open(tempout, "r") as infp:
            write_seed(outfp, infp, seed, empty_sets)

    for tempin in temp_inputs:
        try:
            os.unlink(tempin)
        except OSError:
            pass
    for tempout in temp_outputs:
        try:
            os.unlink(tempout)
        except OSError:
            pass

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
        workdir = workingdirectory(args.algo, args.ndv,
                                   args.nobj, args.eps)

    if not os.path.exists(workdir):
        os.makedirs(workdir)

    if args.outputfile:
        outfp = args.outputfile
    else:
        outfp = open(outputfile(args.algo, args.ndv, 
                                args.nobj, args.eps), "w")

    evaluate_sets(ref, sets, outfp, workdir,
                    args.ndv, args.nobj)
    close()
    outfp.close()

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
