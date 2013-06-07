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

"""
import argparse
import re
from aggregates import Aggregates
import response 
from pfpf import PFPF 
import sys

class BadProblem(Exception):
    def __init__(self, ndvs, nobjs):
        super(BadProblem, self).__init__(
                "Unknown problem {0}_{1}".format(ndvs, nobjs))

def cli():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("ndvs", choices=[18,27],
                        help="number of decision variables",
                        type=int)
    parser.add_argument("nobjs", choices=[3, 10],
                        help="number of objectives",
                        type=int)
    return parser.parse_args()

def twentyseven_from_eighteen_dvs(dvs):
    # CSPD AR (SWEEP) DPROP WINGLD AF SEATW (ELODT) (TAPER)
    sweep = 4.0
    elodt = 3.09
    taper = 0.46
    twentyseven = []
    for aircraft in range(3):
        twentyseven.extend(dvs[aircraft*6:aircraft*6+2])
        twentyseven.append(sweep)
        twentyseven.extend(dvs[aircraft*6+2:aircraft*6+6])
        twentyseven.append(elodt)
        twentyseven.append(taper)
    return twentyseven

def three_from_ten_objs(objs):
    eps = [0.15, 30.0, 6.0, 0.03, 30.0, 
            3000.0, 150.0, 0.3, 3.0, 0.3]
    three = []
    three.append(sum([objs[ii] / eps[ii] for ii in [1,2,5]]))
    three.append(sum([objs[ii] / eps[ii] for ii in [4,6,7,8]]))
    three.append(objs[9])
    return three

def evaluate(transform_dvs, transform_objs):
    model = response.Response()
    agg = Aggregates()
    pfpf = PFPF()

    line = sys.stdin.readline()
    while line:
        dvs = [float(xx) for xx 
               in re.split("[ ,\t]", line.strip())]
        dvs = transform_dvs(dvs)
        outputs = model.evaluate_wide(dvs)
        outputs = agg.convert_row(outputs)
        objectives = agg.minmax(outputs)
        objectives.append(pfpf.pfpf(dvs))
        objectives = transform_objs(objectives)
        constraint = agg.constr_violation(outputs)
        objectives.append(constraint)
        towrite = " ".join([unicode(xx) for xx in objectives])+"\n"
        sys.stdout.write(towrite)
        sys.stdout.flush()
        line = sys.stdin.readline()

def get_transformations(ndvs, nobjs):
    passthrough = lambda x: x
    transform_dvs  = None
    transform_objs = None
    if nobjs == 10:
        transform_objs = passthrough
    elif nobjs == 3:
        transform_objs = three_from_ten_objs
    else:
        raise BadProblem(ndvs, nobjs)

    if ndvs == 27:
        transform_dvs = passthrough
    elif ndvs == 18:
        transform_dvs = twentyseven_from_eighteen_dvs
    else:
        raise BadProblem(ndvs, nobjs)

    return (transform_dvs, transform_objs)

if __name__ == "__main__":
    args = cli()
    td, to = get_transformations(args.ndvs, args.nobjs)
    evaluate(td, to)
    

# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
