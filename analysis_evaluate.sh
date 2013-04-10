#!/bin/sh
source setup.sh
ALGORITHMS="Borg eMOEA"
PROBLEMS="GAA_27_10 GAA_18_10 GAA_27_3 GAA_18_3 GAA_9_9 GAA_6_9 GAA_9_2 GAA_6_2"
SEED_START=1
SEED_END=50

for PROBLEM in ${PROBLEMS}; do
	for SEED in $(seq ${SEED_START} ${SEED_END}); do
		for ALGORITHM in ${ALGORITHMS}; do		
		        NOBJS=`echo ${PROBLEM} | cut -d '_' -f3`

		        if [ "${NOBJS}" == "10" ]; then
				REFSET="GAA_10D.reference"
		        elif [ "${NOBJS}" == "9" ]; then
				REFSET="GAA_9D.reference"
		        elif [ "${NOBJS}" == "3" ]; then
				REFSET="GAA_3D.reference"
		        elif [ "${NOBJS}" == "2" ]; then
				REFSET="GAA_2D.reference"
		        else
		                echo "Undefined number of objectives: ${NOBJS}"
		                exit 1
		        fi

                        NAME=Evaluate_${ALGORITHM}_${PROBLEM}_${SEED}
                        PBS="#PBS -N ${NAME}\n"
                        PBS="${PBS}#PBS -l nodes=1\n"
                        PBS="${PBS}#PBS -l walltime=96:00:00\n"
                        PBS="${PBS}#PBS -o output/${NAME}\n"
                        PBS="${PBS}#PBS -e error/${NAME}\n"
                        PBS="${PBS}cd \$PBS_O_WORKDIR\n"
                        PBS="${PBS}source setup.sh\n"
                        PBS="${PBS}java ${JAVA_ARGS} org.moeaframework.analysis.sensitivity.ResultFileEvaluator --problem ${PROBLEM} --output ${WORK}/${ALGORITHM}_${PROBLEM}_${SEED}.metrics --input ${WORK}/${ALGORITHM}_${PROBLEM}_${SEED}.sets --reference ${WORK}/${REFSET}"
                        echo -e $PBS | qsub
		done
	done
done

