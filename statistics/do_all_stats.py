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

do_all_stats.py

Go into the metrics directory and hit all of the files 
with all of the statistics.  
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
