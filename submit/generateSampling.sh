#!/bin/sh
source setup.sh
MOEAFRAMEWORK_SEED=1337

# the numbers 715 and 228 get the # of Sobol samples closest to 10k
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 715 -p params/eMOEA_Params -o params/eMOEA_Sobol -s $MOEAFRAMEWORK_SEED
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 228 -p params/Borg_Params -o params/Borg_Sobol -s $MOEAFRAMEWORK_SEED
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 715 -p params/NSGAII_Params -o params/NSGAII_Sobol -s $MOEAFRAMEWORK_SEED
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 715 -p params/eNSGAII_Params -o params/eNSGAII_Sobol -s $MOEAFRAMEWORK_SEED
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 500 -p params/MOEAD_Params -o params/MOEAD_Sobol -s $MOEAFRAMEWORK_SEED
 java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 1000 -p params/GDE3_Params -o params/GDE3_Sobol -s $MOEAFRAMEWORK_SEED

#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 71 -p params/eMOEA_Params -o params/eMOEA_Sobol -s $MOEAFRAMEWORK_SEED
#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 22 -p params/Borg_Params -o params/Borg_Sobol -s $MOEAFRAMEWORK_SEED
#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 71 -p params/NSGAII_Params -o params/NSGAII_Sobol -s $MOEAFRAMEWORK_SEED
#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 71 -p params/eNSGAII_Params -o params/eNSGAII_Sobol -s $MOEAFRAMEWORK_SEED
#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 50 -p params/MOEAD_Params -o params/MOEAD_Sobol -s $MOEAFRAMEWORK_SEED
#java $JAVA_ARGS org.moeaframework.analysis.sensitivity.SampleGenerator -m saltelli -n 100 -p params/GDE3_Params -o params/GDE3_Sobol -s $MOEAFRAMEWORK_SEED
