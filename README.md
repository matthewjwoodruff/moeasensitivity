moeasensitivity
===============

Sensitivty analysis on MOEA parameters using MOEAFramework and Python.

Analysis procedes in this order:
- `hv` is for hypervolume calculation
- `statistics` is for statistical summaries of the hv data
- `controlmaps` uses statistics to make colored contour plots of MOEA performance in parameter space.
- `sobol` uses statistics to make radial convergence plots showing Sobol' global 
sensitivity indices for variance in MOEA performance across the parameter space.
