ref 
===================

Generate and combine reference sets for each MOEA / problem.

- `PSOProblemStub.java`, `PSOResultFileMerger.java`, `PSOResultFileReader.java` are for sorting together the different reference sets.  Unlike the sort that's built into MOEAFramework, these preserve the decision variables.
- `submit.py` submits runs for the Java reference set merger
- `combine_refsets.py` combines reference sets for diffent MOEA / problems with compatible objectives

