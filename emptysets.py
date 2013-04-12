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
