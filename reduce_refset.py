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
