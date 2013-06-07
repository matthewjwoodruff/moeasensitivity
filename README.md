moeasensitivity
===============

Sensitivty analysis on MOEA parameters using MOEAFramework and Python.  

Analysis procedes in this order:
- `submit` does a massive number of optimization runs
- `ref` is for reference set computation
- `hv` is for hypervolume calculation
- `statistics` is for statistical summaries of the hypervolume data
- Make plots
    - `controlmaps` uses statistics to make colored contour plots of MOEA 
	hypervolume performance in parameter space.
    - `sobol` uses statistics to make radial convergence plots showing Sobol' global 
	sensitivity indices for variance in MOEA performance across the parameter space.
	Also make first/total order bar charts.
    - `cdf` does shaded bar / dot plots based on the hypervolume data
    - `parallel` does parallel coordinate plots and makes input data files for
	AeroVis scatter plotting

Bonus:
- `contour` shows joint probability density functions for MOEA performance, but it 
    is less informative than I had hoped.  These plots are not used in the paper.

What you have to do by hand: 
- Arrange the Pareto approximation sets files into 
    a sensible folder structure after all of the optimization has been done.  All of the
    analysis from `ref` on assumes a particular folder structure for the approximation 
    sets data.
- Run the analysis scripts in each directory.  I don't have a `makefile` that lets you
    do `make researchpaper`.  Maybe for my next study!
