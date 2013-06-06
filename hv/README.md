hv
===============

Hypervolume computation relies on MOEAFramework being in ./lib/

It also, optionally, relies on the wfg2 executable to compute hypervolume.  
If you don't have it, you're going to want to delete the first line of global.properties.  
(wfg2 makes hypervolume computation *way* faster.)
