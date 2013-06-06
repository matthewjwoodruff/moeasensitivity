from subprocess import Popen
from time import sleep
for ii in range(3079250, 3079652):
    Popen(["qdel", str(ii)])
    sleep(0.2)

