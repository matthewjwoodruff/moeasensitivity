python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 27_10_1.0 -o 27_10_1.0.png -w 0.00389732705522 -b 0.0390303319163
python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 18_10_1.0 -o 18_10_1.0.png -w 0.00389732705522 -b 0.0390303319163
python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 27_3_0.1 -o 27_3_0.1.png -w 0.0522599393295 -b 0.0824581625125
python controlmaps.py Borg,eMOEA,NSGAII,eNSGAII,GDE3 18_3_0.1 -o 18_3_0.1.png -w 0.0522599393295 -b 0.0824581625125
convert 27_10_1.0.png -trim +repage 42_27_10.png
convert 18_10_1.0.png -trim +repage 43_18_10.png
convert 27_3_0.1.png -trim +repage 40_27_3.png
convert 18_3_0.1.png -trim +repage 41_18_3.png
