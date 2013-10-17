ref 
===================

Generate and combine reference sets for each MOEA / problem.

- `PSOProblemStub.java`, `PSOResultFileMerger.java`, `PSOResultFileReader.java` are for sorting together the different reference sets.  Unlike the sort that's built into MOEAFramework, these preserve the decision variables.
- `submit.py` submits runs for the Java reference set merger
- `combine_refsets.py` combines reference sets for diffent MOEA / problems with compatible objectives

## Generating reference sets with `pareto.py`

`````
python pareto.py {Borg,GDE3,NSGAII,eMOEA,eNSGAII}_27_10_1.0* -o 27-36 -d " " --contribution --line-number --output 27_10_1.0.ref -e 0.15 30.0 6.0 0.03 30.0 3000.0 150.0 0.3 3.0 0.3
python pareto.py {Borg,GDE3,NSGAII,eMOEA,eNSGAII}_27_3_0.1* -o 27-29 -d " " --contribution --line-number --output 27_3_0.1.ref -e 0.1 0.1 0.1
python pareto.py {Borg,GDE3,NSGAII,eMOEA,eNSGAII}_18_10_1.0* -o 18-27 -d " " --contribution --line-number --output 18_10_1.0.ref -e 0.15 30.0 6.0 0.03 30.0 3000.0 150.0 0.3 3.0 0.3
python pareto.py {Borg,GDE3,NSGAII,eMOEA,eNSGAII}_18_3_0.1* -o 18-20 -d " " --contribution --line-number --output 18_3_0.1.ref -e 0.1 0.1 0.1
`````
