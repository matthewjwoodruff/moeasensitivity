"""
"""
from statistics import analyze, write_result
import os
import re
import pandas

metricsdir = "/gpfs/scratch/mjw5407/task1/hv"
paramsdir = "/gpfs/work/mjw5407/task1/statistics/params"
outputdir = "/gpfs/scratch/mjw5407/task1/stats"

datafiles = [os.path.join(metricsdir, fn) 
             for fn in os.listdir(metricsdir)
             if re.search("\.hv$", fn) and not
                re.search("^m\.", fn)]

for fn in datafiles:
    print "processing {0}".format(fn)
    data = pandas.read_table(fn, sep=" ")
    algo = os.path.basename(fn).split("_")[0]
    pfilename = os.path.join(paramsdir, algo+"_Params")
    parameters = pandas.read_table(pfilename,
        sep = " ", names = ["name", "low", "high"],
        header = None)
    param_names = parameters.name.values
    parameterizations = pandas.read_table(
        os.path.join(paramsdir, algo+"_Sobol"),
        sep = " ", names = param_names,
        header = None)
    popsize = [name for name in param_names
               if re.search("[Pp]opulationSize", name)][0]

    data = data.join(parameterizations, on=["Set"],
                     how="outer")

    setresults = analyze(data, ["mean", "variance", "q10", 
                             "q50", "q90", "min", "max"])
    for result in setresults:
        write_result(fn, result, outputdir)
    gridresults = analyze(data, ["mean", "variance", "q10", 
                             "q50", "q90", "min", "max"],
                              [popsize, "maxEvaluations"],
                              [334, 333334])
    for result in gridresults:
        write_result(fn, result, outputdir)


# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
