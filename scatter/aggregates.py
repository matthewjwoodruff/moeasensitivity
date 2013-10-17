import sys
import re
from numpy import array as ndarray
from numpy import reshape
from numpy import apply_along_axis 
from numpy import nan
import numpy

class Aggregates(object):
    def __init__(self):
        self.constraints = ndarray([
             [75, 2200, 80, 2, 450,  nan, -2000, nan, nan ],
             [75, 2200, 80, 2, 475,  nan, -2000, nan, nan ],
             [75, 2200, 80, 2, 500,  nan, -2000, nan, nan ]])
        self.absconstraints = numpy.abs(self.constraints)
        self.constrained = numpy.isnan(self.constraints)
        self.goals = ndarray([
             [nan, 1900, 60, nan, 450, 41000, -2500, -17, -200],
             [nan, 1950, 60, nan, 400, 42000, -2500, -17, -200],
             [nan, 2000, 60, nan, 350, 43000, -2500, -17, -200] ])
        self.goaled = numpy.isnan(self.goals)
        self.minimize = ndarray([0, 0, 0, 0, 0, 0, 1, 1, 1])
        self.maximize = 1 - self.minimize

    def minmax(self, row):
        """
        Args: row is 27 responses in 3 groups of 9 (one for
            each of the 2, 4, and 6 seat aircraft)
        Returns: 9 minmax objectives
        """
        return numpy.max(reshape(row, (3,9)), 0)

    def constr_violation(self, row):
        performance = reshape(row, (3,9))
        violations = (performance - self.constraints)\
                     / self.absconstraints
        violations = numpy.max(ndarray([numpy.zeros((3,9)),
                                        violations]), 0)
        cv = numpy.ma.masked_array(
                violations, self.constrained
                ).sum()
        return cv

    def goal_attainment(self, row):
        # deviation function: (attained - goal) / attained for min
        #                     (goal - attained) / goal for max
        performance = reshape(row, (3, 9))
        denominator = self.goals * self.minimize \
                      + performance * self.maximize
        violations = (performance - self.goals) / denominator
        violations = numpy.max(ndarray([numpy.zeros((3,9)),
                                        violations]), 0)
        zed = numpy.ma.masked_array(
            violations, self.goaled
            ).sum()

        return zed

    def convert_row(self, row):
        return row - row * numpy.tile(self.minimize, 3) * 2

def run_aggregation():

    line = sys.stdin.readline()
    agg = Aggregates()

    while line:
        # read 27 responses from STDIN:
        # NOISE2 WEMP2 DOC2 ROUGH2 WFUEL2 PURCH2 RANGE2 LDMAX2 VCMAX2 
        # NOISE4 WEMP4 DOC4 ROUGH4 WFUEL4 PURCH4 RANGE4 LDMAX4 VCMAX4 
        # NOISE6 WEMP6 DOC6 ROUGH6 WFUEL6 PURCH6 RANGE6 LDMAX6 VCMAX6

        # convert line to row
        row = ndarray(
           [float(xx) for xx in re.split("[\t ,]", line.strip())]
           )
        # change all responses to minimization
        row = agg.convert_row(row)
        # get minmax objectives
        minmaxobjs = agg.minmax(row)
        # compute constraint violation
        cv = agg.constr_violation(row)
        # compute aggregate performance objective "zed"
        zed = agg.goal_attainment(row)
        outputline = [unicode(xx) for xx in minmaxobjs] + [unicode(zed), unicode(cv)]
        print( " ".join(outputline))

        line = sys.stdin.readline()

if __name__ == '__main__': run_aggregation()


# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
