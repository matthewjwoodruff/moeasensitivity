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
import sys
import re
from numpy import array as ndarray
from numpy import concatenate, apply_along_axis
from numpy import reshape

class Response(object):
    def __init__(self):
        self.matrix = self.read_matrix("coefficient_matrix.txt")
        self.matrixoffsets = {"2":0,"4":9,"6":18}
        self.translate = ndarray([0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73])
        self.scale = ndarray([0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27])

    def read_matrix(self, filename):
        """
        It's worth remembering what the matrix is, exactly.
        Each row is the coefficients for a response.
        Each column is the DVs to which they apply.
        We're assuming that we're generating the design
        vector from the DVs in a consistent way:
        constant, linear terms, interactions, squares
        """
        matrix = []
        with open(filename, 'rb') as fp:
            next(fp) #header
            for line in fp:
                row = line.decode().strip().split("\t")
                row.pop(0) # response name
                matrix.append([float(xx) for xx in row])

        two = ndarray(matrix[0:9])
        four = ndarray(matrix[9:18])
        six = ndarray(matrix[18:27])

        return [two, four, six]

    def get_interactions(self, dvs):
        """
        Standard order for interactions:
        All interactions with the first dv, then all
        remaining interactions for the second dv, etc.
        """
        if len(dvs) == 0: return []
        interactions = self.get_interactions(dvs[1:])
        return [dvs[0]*dv for dv in dvs[1:]] + interactions

    def design_vector(self, dvs):
        desvec = [[1], dvs, self.get_interactions(dvs), dvs ** 2]
        return concatenate(desvec)

    def evaluate(self, dvs, pax):
        dvs = ndarray(dvs)
        dvs = (dvs - self.translate) / self.scale
        design = self.design_vector(dvs)
        return self.matrix[int(pax) // 2 - 1].dot(design)

    def evaluate_wide(self, dvs):
        dvs = reshape(ndarray(dvs), (3,9))
        dvs = (dvs - self.translate) / self.scale
        two = self.design_vector(dvs[0])
        four = self.design_vector(dvs[1])
        six = self.design_vector(dvs[2])
        return concatenate([self.matrix[0].dot(two),
                            self.matrix[1].dot(four),
                            self.matrix[2].dot(six)])
               

def run_response():
    # determine which seats to compute
    seats = [ss for ss in sys.argv if
                 ss in ['2','4','6']]

    if len(seats) == 0:
        message = "  usage: python response.py [2] [4] [6]"
        message += "\n  must specify a number of seats"
        message += "\n  examples:"
        message += "\n  python response.py 6"
        message += "\n  python response.py 2 4 6"
        print(message)
        exit(1)

    driver = Response()

    ndvs = 9 # 9 decision variables per aircraft
    totalndvs = ndvs * len(seats)

    nresp = 9 # 9 responses per aircraft
    respoffset = {"2":nresp*0,"4":nresp*1,"6":nresp*2}

    if totalndvs == 27:
        line = sys.stdin.readline()
        while line:
            variables = [float(xx) for xx in 
                           re.split("[ ,\t]", line.strip())]
            
            if(totalndvs != len(variables)):
                print("Defective inputs!  Got {}, expected {}.".format(
                  len(variables), totalndvs))
                exit(1)
            outputs = driver.evaluate_wide(variables)

            # write response to stdout
            print("\t".join([unicode(xx) for xx in outputs]))

            # get next line
            line = sys.stdin.readline()
        

    else:
        # main loop
        line = sys.stdin.readline()
        while line:
            # take dvs from stdin
            variables = [float(xx) for xx in 
                           re.split("[ ,\t]", line.strip())]
            
            if(totalndvs != len(variables)):
                print("Defective inputs!  Got {}, expected {}.".format(
                  len(variables), totalndvs))
                exit(1)

            outputs = []
            # for each number of seats
            for seat in seats:
                # compute design vector from decision variables
                dvs = variables[0:ndvs]
                variables[0:ndvs] = []
                outputs += driver.evaluate(dvs, seat)

            # write response to stdout
            print("\t".join([unicode(xx) for xx in outputs]))

            # get next line
            line = sys.stdin.readline()

if __name__ == '__main__': run_response()

# vim:ts=4:sw=4:expandtab:fdm=indent:ai
