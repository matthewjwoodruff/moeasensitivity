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
resubmit.py
"""
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
