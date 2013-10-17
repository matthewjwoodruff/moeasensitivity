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
        return ["F1", "F2", "F3"]
    elif nobj == 10:
        return "NOISE WEMP DOC ROUGH WFUEL PURCH RANGE LDMAX VCMAX PFPF".split(" ")
    else:
        raise Exception("Can't handle {0} objectives".format(nobj))

def outputnames():
    base = objnames(10)[0:9]
    names = []
    for seats in ["2", "4", "6"]:
        names.extend([name + seats for name in base])
    return names


def get_data(ndvs, nobj, eps, **kwargs):
    dirname = kwargs.get("dirname", ".")
    filename = "{0}_{1}_{2:.1f}.ref".format(ndvs, nobj, eps)
    names = dvnames(ndvs) + objnames(nobj) + ["file", "line"]
    table = pandas.read_table(os.path.join(dirname, filename),
                              sep = " ", header=None, names=names)
    return table

def minify(table):
    table["F2"] = -table["F2"]
    for suffix in ["", "2", "4", "6"]:
        table["RANGE"+suffix] = -table["RANGE"+suffix]
        table["LDMAX"+suffix] = -table["LDMAX"+suffix]
        table["VCMAX"+suffix] = -table["VCMAX"+suffix]

def reevaluate(ndvs, nobj, eps):
    model = response.Response()
    agg = Aggregates()
    pfpf = PFPF()
    table = get_data(ndvs, nobj, eps)
    names = dvnames(ndvs)
    dvs = list(table[names].values)
    if ndvs == 18:
        dvs = [aviation.twentyseven_from_eighteen_dvs(row)
               for row in dvs]

    dvs = [list(row) for row in dvs]
    outputs = [model.evaluate_wide(row) for row in dvs]

    ten = [list(agg.minmax(row)) for row in outputs]
    tenth = [pfpf.pfpf(row) for row in dvs]
    for row, pfpf in zip(ten, tenth):
        row.append(pfpf)
    three = [aviation.three_from_ten_objs(row) for row in ten]

    newtable = dvs
    for row, a, b, c in zip(newtable, outputs, ten, three):
        row.extend(a)
        row.extend(b)
        row.extend(c)
    names = dvnames(27) + outputnames() + objnames(10) + objnames(3)

    df = pandas.DataFrame(data = newtable, columns=names)
    minify(df)
    return df
    
def aviz(table):
    """
    Put into aerovis format
    """
    lines = []
    lines.append("# Nondominated Solutions: {0}".format(len(table)))
    lines.append("# <DATA_HEADER> RS, Cum_Gen, {0}".format(
                    ", ".join(list(table.columns))))
    lines.append("# <GEN_HEADER> Cum_Gen")
    lines.append("#")
    lines.append("1")
    lines.append("#")
    for ii in range(len(table)):
        row = list(table.irow(ii))
        lines.append("\t".join(["1\t1", "\t".join([str(val) 
                                                  for val in row])]))
    return "\n".join(lines)

def reevaluate_all():
    problems = [(27, 10, 1.0), (27, 3, 0.1), 
                (18, 10, 1.0), (18, 3, 0.1)]
    tables = [reevaluate(d, o, e) 
              for d, o, e 
              in problems]
    for table, problem in zip(tables, problems):
        table.problem = problem
    return tables

def cli():
    # 27 dv contributes all the ref solutions
    data = reevaluate_all()

    for table in data:
        with open("{0}_{1}_{2}.out".format(*table.problem), 'w') as fp:
            fp.write(aviz(table))
        table.to_csv(
            "{0}_{1}_{2}.recalc".format(*table.problem), sep=" ",
            header=False, index=False)

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
