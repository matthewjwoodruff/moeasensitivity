sobol
========================

Sobol' analysis using MOEAframework.  

- `sobol.py`: perform the analysis.  Results in a bunch of reports files.
    This takes a considerable amount of time due to the large number of reports files generated..
- `tabulate.py`: gather reports files for each algorithm/problem together into a table.  Each column corresponds to a report file.
- `analysis.py`: wraps up `sobol.py` and `tabulate.py`, lets you do both at once
- `radialconvergence.py`: make radial convergence plots of the sensitivity data.
- `report.py`: make vertical bar charts
- `barcharts.py`: make horizontal bar charts
- `barcharts.sh`: create barcharts used in the paper
