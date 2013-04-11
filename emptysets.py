import re
import argparse

def find_empty_sets(stream):
    return []

def get_args():
    parser  = argparse.ArgumentParser()
    parser.add_argument("filename", 
                        type=argparse.FileType("r"),
                        help="sets file to scan for empty "\
                             "solution sets"
                       )

def cli():
    args = get_args()
    print " ".join(find_empty_sets(args.filename))

if __name__ == "__main__":
    cli()

# vim:ts=4:sw=4:expandtab:ai:colorcolumn=60:number:fdm=indent
