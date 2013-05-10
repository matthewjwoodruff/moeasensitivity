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
recalc.py

Recompute both three and ten objective solutions.
"""
    
import pandas
import aviation
import response
from aggregates import Aggregates
from pfpf import PFPF
import os

def dvnames(ndvs):
    dvs = "CSPD AR SWEEP DPROP WINGLD AF SEATW ELODT TAPER"
    dvs = dvs.split(" ")
    if ndvs == 18:
        dvs = [dv for dv in dvs if dv not in "SWEEP ELODT TAPER"]
    elif ndvs == 27:
        pass
    else:
        raise Exception("Can't handle {0} DVs".format(ndvs))

    names = []
    for seats in ["2", "4", "6"]:
        names.extend([name+seats for name in dvs])
    return names

def objnames(nobj):
    if nobj == 3:
        return ["F1", "F2", "PFPF"]
    elif nobj == 10:
        return "NOISE WEMP DOC ROUGH WFUEL PURCH RANGE LDMAX VCMAX PFPF"    
    else:
        raise Exception("Can't handle {0} objectives".format(nobj))

def get_data(ndvs, nobj, eps):
    dirname = "/gpfs/scratch/mjw5407/task1/ref"
    filename = "m.{0}_{1}_{2}".format(ndvs, nobj, eps)
    names = dvnames(ndvs) + objnames(nobj)
    table = pandas.read_table(os.path.join(dirname, filename),
                              sep = " ", header=None, names=names)
    return table

def reevaluate(ndvs, nobj, eps):
    model = response.Response()
    agg = Aggregates()
    pfpf = PFPF()
    table = get_data(ndvs, nobj, eps)
    dvnames = dvnames(ndvs)
    dvs = table[dvnames]
    if ndvs == 18:
        dvs = [aviation.twentyseven_from_eighteen_dvs(row)
               for row in dvs]

    outputs = [model.evaluate_wide(row) for row in dvs]
    nine = [agg.minmax(row) for row in outputs]
    tenth = [pfpf.pfpf(row) for row in dvs]
    ten = [row.append(pfpf) for row, pfpf in zip(nine, tenth)]
    three = [aviation.three_from_ten_objs(row) for row in ten]

    return dvs, ten, three
    
    
   
    

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
