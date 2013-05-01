import sys
import os
import re
import textwrap
import argparse

class TabulationError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __unicode__(self):
        return unicode(self.value)

def checkfirstline(fn):
    """ 
    sure, it's slow. but it's not like we're 
    doing this to a whole lot of files
    """
    expected = "Parameter	Sensitivity [Confidence]"
    fp = open(fn, 'rb')
    firstline = fp.readline().strip()
    return firstline == expected

def get_matching_files(filenames, response, tag):
    return [
                [response, tag, filename] 
                for filename in filenames
                if response in filename 
                   and tag in filename 
                   and checkfirstline(filename)
            ]

def tabulate_report(report):
    orders = ["First-Order Effects", "Total-Order Effects", 
              "Second-Order Effects", ]

    rex = re.compile(
        '(^  ([a-zA-Z0-9]+)( \* [a-zA-Z0-9]+)?) '
        +'(-?[0-9]+\.[0-9]+(E[-][0-9]+)?) \[(.*)\]')

    rows = []
    ifp = open(report[2], 'rb')
    line = ifp.readline()
    response = report[0]
    tag = report[1]

    while line:
        line = ifp.readline()
        if line.strip() in orders:
            order = line.split("-")[0] 

        matches = re.search(rex, line)
        if matches:
            # groups (0) is the name of the input
            groups = matches.groups()
            inputname = groups[1].strip()
            if groups[2]:
                interaction = groups[2].strip()[2:]
            else:
                interaction = ""
            sensitivity = groups[3].strip()
            confidence = groups[5].strip()
            rows.append([inputname, interaction, response, tag,
                         order, sensitivity, confidence])
    return rows

def tabulate(responses, tags):
    """
    Read sensitivity data from files and convert it to tabular form

    Args:
        responses: a list of responses to look for in the filenames
        tags: a list of tags to distinguish responses, or None
    """
    err = "\nCould not distinguish {0}\nTags: {1}\nResponse: {2}\n"
    reports = []
    filenames = os.listdir('.')
    if tags:
        searchtags = tags
    else: 
        searchtags = filenames

    for tag in searchtags:
        for response in responses:
            matches = get_matching_files(
                        filenames, response, tag)
            if len(matches) == 1:
                reports.extend(matches)
            elif len(matches) > 1:
                multiples = [filename for response, tag, filename
                             in matches]
                raise TabulationError(err.format(
                   ", ".join(multiples), ", ".join(tags), response))
    rows = []
    for report in reports:
        rows.extend(tabulate_report(report))
        
    header = ["input","interaction","response","tag",
              "order","sensitivity","confidence"]
    return (header, rows)

def cli():
    """
    Command-line interface for making a tabular summary
    of sensitivity indices.
    """
    description = textwrap.dedent('''\
        {0}: create a table of sensitivity indices
        ------------------------------------------------------------
            Create a table of sensitivity indices from separate
        data files such as those generated by the MOEAFramework
        sensitivity analysis.  Each input file contains the 
        sensitivity indices for all of the inputs to a single 
        response.
            We look for all filenames containing any of the 
        specified response names.  If tags are specified, only
        filenames containing these tags are summarized, and 
        the tags are used to differentiate multiple files 
        containing indices for the same response.  Otherwise,
        we will take the entire filename as a tag.

        Usage examples:

        Example 1: you have files NOISE_sobols.txt and 
            WEMP_sobols.txt.  This example makes a single table
            of the data for both responses, using the filenames
            to populate the tag column.
        python {0} NOISE WEMP > table.txt

        Example 2: you have files sobols_NOISE_10k.txt, 
            sobols_WEMP_10k.txt, sobols_NOISE_65k.txt, and
            sobols_WEMP_65k.txt.  This example makes a single table
            of the data from all four files, using the filenames
            to populate the tag column.
        python {0} NOISE WEMP > table.txt

        Example 3: in addition to the files in Example 2, you have
            sobols_WEMP_8k.txt, but you don't want it to appear in
            the summary table.  The resulting table will use "10k"
            and "65k" for the tag column.
        python {0} NOISE WEMP -t 10k 65k > table.txt

        '''.format(sys.argv[0]))

    parser = argparse.ArgumentParser(description=description,
            formatter_class = argparse.RawDescriptionHelpFormatter,
            usage=("{0} [-h] response [response ...] "
                   +"[-t TAGS [TAGS ...]]").format(sys.argv[0]))
    parser.add_argument("response",
        help="Names of the responses as they appear in filenames, "
             + "separated by spaces",
        nargs = "+")
    parser.add_argument("-t", "--tags",
        help="Tags to distinguish responses, separated by spaces.",
        nargs = "+")
    
    # parse the command-line arguments
    args = parser.parse_args()

    # tabulate!
    header, rows = tabulate(args.response, args.tags)

    # print the table
    print "\t".join(header)
    for row in rows:
        print "\t".join(row)
        
if __name__ == "__main__":
    """
    Dummy main function.

    Run the command-line interface
    """
    cli()
# vim:sw=4:ts=4:expandtab:fdm=indent:colorcolumn=68:ai
