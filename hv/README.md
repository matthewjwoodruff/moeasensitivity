hv
===============

Hypervolume computation relies on MOEAFramework being in ./lib/

It also, optionally, relies on the wfg2 executable to compute hypervolume.  
If you don't have it, you're going to want to delete the first line of global.properties.  
(wfg2 makes hypervolume computation *way* faster.)

# Reference Set Metrics

## Ten Objectives

Hypervolume  | GenerationalDistance | InvertedGenerationalDistance | Spacing            | EpsilonIndicator   | MaximumParetoFrontError
-------------|----------------------|------------------------------|--------------------|--------------------|------------------------
0.0589790584 | 0.0                  | 0.006157856177705548         | 26.391000474820522 | 0.6025774824088875 | 0.0

## Three Objectives


Hypervolume  | GenerationalDistance | InvertedGenerationalDistance | Spacing             | EpsilonIndicator    | MaximumParetoFrontError
-------------|----------------------|------------------------------|---------------------|---------------------|------------------------
0.7900893716 | 0.0                  | 0.03378198615318             | 0.37616528308071046 | 0.17441343175248455 | 0.0
