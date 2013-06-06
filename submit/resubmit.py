import argparse
from subprocess import Popen, PIPE
import time

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numberofjobs", default = 24, 
                    type = int,
                    help = "number of times to repeat")
parser.add_argument("-i", "--interval", default = 60.0,
                    type = float,
                    help = "number of minutes to wait")
args = parser.parse_args()
for ii in range(args.numberofjobs):
    print "Running submit.py ({0})".format(ii)
    child = Popen(["python", "submit.py", "-a", "eNSGAII", 
                   "-p", "27_10", "-s", "50,50"], stdout=PIPE)
    line = child.stdout.readline()
    while line:
        line = line.strip()
        print line
        line = child.stdout.readline()
    #print "Running statusplot.py ({0})".format(ii)
    #child = Popen(["python", "statusplot.py"], stdout=PIPE)
    #print child.stdout.read()
    print " --- "
    print time.strftime("%Y-%m-%d %H:%M:%S")
    print "Waiting for {0} minutes".format(args.interval)
    print " --- "
    time.sleep(args.interval * 60)
