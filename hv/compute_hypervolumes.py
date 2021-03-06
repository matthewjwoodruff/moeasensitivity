"""
Copyright (C) 2013 Joseph Kasprzyk, Matthew Woodruff and others.

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

compute_hypervolumes.py

Use MOEAFramework and the wfg2 hypervolume computation to
compute hypervolume attainment for every run of an MOEA
parameter sensitivity study.

Paths default to the ones most convenient for the author's
purposes.  You should change them, or at least override
them on the command line.

"""
from subprocess import Popen, PIPE
import re
import glob
import os
import argparse
from emptysets import find_empty_sets
from reduce_refset import awkscript

class PathError(Exception):
    pass

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
    parser.add_argument("-d", "--setsdirectory",
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
    parser.add_argument("-s", "--seed", type=int,
                        help="run a single seed and leave "\
                             "the result sitting in the "\
                             "working directory.  User "\
                             "must patch up the aggregate "\
                             "file manually.")

    return parser.parse_args()

def outputfile(algo, ndv, nobj, eps, seed=None):
    fn = [algo, str(ndv), str(nobj), str(eps)]
    if seed is not None:
        fn.append(str(seed))
        dirname = workingdirectory(algo, ndv, nobj, eps)
    else:
        dirname = "/gpfs/scratch/mjw5407/task1/hv/"

    fn = "_".join(fn) + ".hv"
    return os.path.join(dirname, fn)

def referencefilename(nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/ref/"\
           "m.{0}_{1}.ref".format(nobj, eps)

def setsdirectory(algo, ndv, nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/sets/"\
           "{0}_{1}_{2}_{3}".format(algo, ndv, nobj, eps)

def workingdirectory(algo, ndv, nobj, eps):
    return "/gpfs/scratch/mjw5407/task1/hv/temp/"\
           "{0}_{1}_{2}_{3}".format(algo, ndv, nobj, eps)

def strip_dvs(ndv, nobj, setsfile, tempfile):
    awktext = awkscript(ndv, nobj, tempfile)
    cml = ["awk", awktext, setsfile]
    print " ".join(cml)
    child = Popen(cml)
    child.wait()
    sedtext = ["sed", "-i", "-e", "/^ *$/d", tempfile]
    child = Popen(sedtext)
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
                        seed, counter, emptymetrics))
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

    return temp_inputs, temp_outputs

def cleanup(temp_inputs, temp_outputs): 
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
    if args.seed is not None:
        sets = [aset for aset in sets if re.search(
                "_{0}.sets".format(args.seed), aset)]

    print "sets {0}".format("\n".join(sets))
    if args.workingdirectory:
        workdir = args.workingdirectory
    else:
        workdir = workingdirectory(args.algo, args.ndv,
                                   args.nobj, args.eps)

    if not os.path.exists(workdir):
        os.makedirs(workdir)

    if args.outputfile:
        outfp = args.outputfile
    elif args.seed is None:
        fn = outputfile(args.algo, args.ndv, 
                        args.nobj, args.eps)
        if os.path.exists(fn):
            msg = "{0} exists, specify explicitly to "\
                  "clobber".format(fn)
            raise PathError(msg)
        outfp = open(fn, "w")
    else:
        fn = outputfile(args.algo, args.ndv, 
                        args.nobj, args.eps, args.seed)
        if os.path.exists(fn):
            msg = "{0} exists, specify explicitly to "\
                  "clobber".format(fn)
            raise PathError(msg)
        outfp = open(fn, "w")
    try:
        tin, tout = evaluate_sets(ref, sets, outfp, workdir,
                                  args.ndv, args.nobj)
        if args.seed is None:# one-seed run leaves working files
            cleanup(tin, tout)
    finally:
        outfp.close()

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
