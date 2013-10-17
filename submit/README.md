submit
======

## What I used for running this study:

- `generateSampling.sh`
- `params`
- `submit.py` along with a Python interpreter
- `MOEAFramework` unpacked into a `lib` directory, along with a Java runtime
- An implementation of the Borg MOEA compatible with MOEAFramework
- A big computing cluster with a PBS job scheduler
- Subdirectories named `output` and `error` for the PBS output and error streams
- Four months or so of computer time.

## Epsilons

* 3 objectives: (0.1,0.1,0.1)
* 10 objectives:  (0.15,30.0,6.0,0.03,30.0,3000.0,150.0,0.3,3.0,0.3)

## How:
~~~~
    sh generatesampling.sh
    python submit.py -a Borg,eMOEA,NSGAII,eNSGAII,GDE3 -p 27_10,18_10,27_3_0.1,18_3_0.1 -s 1,50
~~~~

Note that you'll have to run `submit.py` *again and again* to get all 10,000 parameterizations to complete for each MOEA, unless your job scheduler lets you submit jobs that run for weeks.  Or perhaps you're living in a golden future when this kind of study can be done in the time it takes to drink your morning coffee.  Running `submit.py` repeatedly works because MOEAframework can tell how many parameterizations have already been run, and it picks up where it left off.

## Bonus material:
- `OneParameterization.java` in case you want to run a particular parameterization rather than the full Sobol' sequence
- `statusplot.py` to keep track of how much of the computation has been done
- `unsubmit.py` demonstrates how to kill a whole bunch of jobs, in case you have second thoughts after running `submit.py`
- `resubmit.py` so you can keep the PBS queue full of your jobs at all times




