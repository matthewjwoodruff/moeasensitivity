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
reduce_refset.py

Mainly, produce an awk script that will strip decision 
variables from a file containing solution sets, while 
preserving the lines that delimit the solution sets.

If invoked at the command line, print out the awk script.

"""

import argparse

def awkscript(ndv, nobj, otpt):
    percents = ["%s"]*nobj
    dollars = ["${0}".format(ndv+ii+1) for ii in range(nobj)]
    script = ";".join(['BEGIN {{FS=" "}}',
             '/^# *$/ {{print $0 > "{0}"}}',
             '/^# *\\// {{print $0 > "{0}"}}',
             '/^[0-9][^a-z]*$/ {{printf "{1}\\n",{2}  > "{0}"}}'])
    return script.format(otpt, " ".join(percents), 
                               ",".join(dollars))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("ndv", type=int)
    parser.add_argument("nobj", type=int)
    parser.add_argument("otpt")
    return parser.parse_args()

def cli():
    args = get_args()
    text = awkscript(args.ndv, args.nobj, args.otpt)
    print "awk '{0}'".format(text)

if __name__ == "__main__":
    cli()
# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
