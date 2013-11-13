controlmaps
===============

Control maps for hypervolume.  That is, one MOEA parameter on the abscissa,
another on the ordinate, of a colored contour plot.  Right now popsize vs
nfe is hard coded, but should be easy to change.  Works well with the 
ipython pylab notebook.  Layout requires too much hand-tuning right now, 
but looks decent.

###Command Lines

``````
python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 27_10_1.0,18_10_1.0 -o ten.png
python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 27_3_0.1,18_3_0.1 -o three.png
``````

