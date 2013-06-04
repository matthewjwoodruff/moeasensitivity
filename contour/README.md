countour
========

Plot a joint PDF of hypervolume attainment.
    Each x,y location corresponds the performance of a particular parameterization.
    Since there are approximately 10,000 paramterizations times 50 seeds, there are
    approximately 500,000 points, which is too many for overplotting to represent.
    This plot uses density contours with a resolution of 0.001 on each axis to show
    the density of points for each x,y combination of performance.

The idea for this plot is that it would show how likely it is for an MOEA to perform
    consistently across parameterizations, to give the user some idea of reliability.
