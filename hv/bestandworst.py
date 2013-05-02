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

bestandworst.py

Report the best and worst values for each objective, from
among all solutions in all sets in a file.
"""
import os
import re
import argparse
import sys

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        type = argparse.FileType("r"),
                        help = "A file containing solution sets")
    parser.add_argument("first", type=int,
                        help = "Column index of first objective")
    parser.add_argument("last", type=int,
                        help = "Column index of last objective")
    return parser.parse_args()

def scan(stream, first, last):
    counter = 0
    best = None
    worst = None
    line = True
    while line != '':
        line = stream.readline()
        if line is '':
            break
        if not re.match("[0-9.\-eE ]+", line):
            continue
        row = line.split(" ")
        if len(row) < last + 1:
            continue
        row = [float(val) for val in row]
        if best is None:
            best = row[first:last+1]
            worst = row[first:last+1]
        else:
            best = [min(best[ii], row[first+ii]) 
                    for ii in range(len(best))]
            worst = [max(worst[ii], row[first+ii]) 
                     for ii in range(len(worst))]
        counter += 1
    return best, worst

def cli():
    args = get_args()
    best, worst = scan(args.filename, args.first, args.last)
    print best
    print worst

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=68:number:fdm=indent
