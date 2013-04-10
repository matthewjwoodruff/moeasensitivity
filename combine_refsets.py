"""
TODO: CONTRIBUTION
"""
from subprocess import Popen, PIPE
import re
import glob
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("nobj")
    parser.add_argument("epsilon_scaling")
    parser.add_argument("-a", "--algorithm")
    parser.add_argument("-d", "--ndv")
    parser.add_argument("-i", "--input_directory",
                        default="/gpfs/scratch/mjw5407/task1/ref")
    parser.add_argument("-o", "--output_directory",
                        default="/gpfs/scratch/mjw5407/task1/ref")
    parser.add_argument("-c", "--contribution", action='store_true',
                        help="tabulate contributions to the "\
                             "final reference set")
                        
    return parser.parse_args()

def input_filenames(algorithm, ndv, nobj, eps, dirname):
    """
    You almost certainly don't want to specify both algorithm
    and ndv, because the input files are already alg_ndv_nobj_eps.
    So you'd just be merging a single file.
    """
    if not algorithm:
        algorithm = "*"
    if not ndv:
        ndv = "*"
    pattern = "{0}_{1}_{2}_{3}.ref".format(
               algorithm, ndv, nobj, eps)
    return glob.glob(os.path.join(dirname, pattern))

def output_filename(algorithm, ndv, nobj, eps, dirname):
    if algorithm:
        algorithm = "{0}_".format(algorithm)
    else:
        algorithm = ""
    if ndv:
        ndv = "{0}_".format(ndv)
    else:
        ndv = ""

    fn = "m.{0}{1}{2}_{3}.ref".format(algorithm, ndv, nobj, eps)
    return os.path.join(dirname, fn)

def epsilons(nobj, eps):
    return {
        "10_1.0": "0.15,30.0,6.0,0.03,30.0,"\
                  "3000.0,150.0,0.3,3.0,0.3",
        "3_1.0":  "1.0,1.0,1.0",
        "3_0.1":  "0.1,0.1,1.0"
    }["{0}_{1}".format(nobj,eps)]


def commandline(ndv, eps, sets, outputfn):
    classpath = ["./lib/{0}".format(fn) for fn in os.listdir("lib") 
                 if re.search("\.jar$", fn) ]
    classpath.append(".")
    cml = ["java", "-Xmx1g", "-server", "-classpath", 
                                        ":".join(classpath)]

    cml.append("PSOResultFileMerger")
    if not ndv:
        ndv = 0

    cml.extend( [
        "--vars", str(ndv),
        "--epsilon", eps, "--output", outputfn,
        "--dimension", str(len(eps.split(",")))
        ] )
    cml.extend(sets)

    return cml

def compare(row1, row2, tol=1e-5):
    """
    return true if close to equal
    """
    if not len(row1) == len(row2):
        return False
    pairs = zip(row1, row2)
    same = True
    for xx, yy in pairs:
        if yy == 0.0:
            if not xx == 0.0:
                return False
        elif abs(xx / yy - 1.0) > tol:
            return False

    return same

def linetorow(line):
    return [float(val) for val in line.strip().split(" ")]

def rowtoline(row):
    return " ".join([str(val) for val in row])

def contribution(sets, refset, refdvs):
    """
    I think this is inescapably n^2
    But it's fast enough and it works.
    """
    contribfile = re.sub("m\.", "c.", refset)
    ref = []
    with open(refset, "r") as fp:
        line = fp.readline()
        while line:
            row = linetorow(line)
            ref.append(row)
            line = fp.readline()
            

    matches = []
    for _ in range(len(ref)):
        matches.append(list())
    for aset in sets:
        attributes = os.path.basename(aset).split("_")
        ndv = int(attributes[1])
        if ndv == refdvs:
            offset = 0
            refoffset = 0
        else:
            offset = ndv
            refoffset = refdvs

        with open(aset, "r") as fp:
            line = fp.readline()
            while line:
                row = linetorow(line)
                for ii in range(len(ref)):
                    if compare(ref[ii][refoffset:], row[offset:]):
                        matches[ii].append(aset)
                line = fp.readline()

    with open(contribfile, "w") as fp:
        for ref, matches in zip(ref, matches):
            fp.write(rowtoline(ref))
            fp.write(" ")
            fp.write(",".join(matches))
            fp.write("\n")
            
    

def cli():
    args = get_args()
    sets = input_filenames(args.algorithm, args.ndv, 
                           args.nobj, args.epsilon_scaling, 
                           args.input_directory)
    eps = epsilons(args.nobj, args.epsilon_scaling)
    outputfn = output_filename(args.algorithm, args.ndv,
                           args.nobj, args.epsilon_scaling,
                           args.output_directory)
    cml = commandline(args.ndv, eps, sets, outputfn)
    child = Popen(cml, stdout=PIPE)
    child.stdout.read()

    if args.contribution:
        if args.ndv:
            contribution(sets, outputfn, int(args.ndv))
        else:
            contribution(sets, outputfn, 0)

    #print " ".join(cml)

if __name__ == "__main__":
    cli()
