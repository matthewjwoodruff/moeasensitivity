python barchart.py sens Borg borg -k  -W 0.35 -H 1.0
python barchart.py sens eMOEA,NSGAII,eNSGAII,GDE3 others -W 0.35 -H 1.0
python barchart.py sens Borg borg -k -W 0.35 -H 1.0 -v
python barchart.py sens eMOEA,NSGAII,eNSGAII,GDE3 others -W 0.35 -H 1.0 -v
convert borg.png -trim +repage 50_borg.png
convert others.png -trim +repage 51_others.png
