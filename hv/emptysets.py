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

emptysets.py

Scan through a MOEAFramework output file containing 
solution sets.  Identify empty solution sets.
"""
import re
import argparse

class LineFormatError(Exception):
    pass

def find_empty_sets(stream):
    empties = []
    counter = 0
    informational = re.compile("^# +[A-Za-z0-9]")
    separator = re.compile("^# */?")
    data = re.compile("^[0-9]")
    blank = re.compile("^ *$")

    started = False
    line = True
    separator_last = False
    while line:
        line = stream.readline()
        if separator.search(line):
            if started:
                if separator_last:
                    empties.append(counter)
                counter += 1
                separator_last = True
        elif data.search(line):
            started = True
            separator_last = False
        elif informational.search(line):
            pass
        elif blank.search(line):
            pass
        else:
            msg = "Unknown line format '{0}'".format(line)
            raise LineFormatError(msg)
                    
    return empties, counter

def get_args():
    parser  = argparse.ArgumentParser()
    parser.add_argument("filename", 
                        type=argparse.FileType("r"),
                        help="sets file to scan for empty "\
                             "solution sets"
                       )
    return parser.parse_args()

def cli():
    args = get_args()
    empties, counter = find_empty_sets(args.filename)
    print "{0}: {1}".format(counter, 
                    " ".join([str(val) for val in empties]))

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
