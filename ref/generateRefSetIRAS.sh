#!/bin/bash
PROBLEM=problem7
DIMENSION=7
EPSILON="0.005,0.005,0.005,0.005,0.005,0.005,0.005"

NVARS=4

JAVA_ARGS="-Xmx128m -classpath MOEAFramework-1.12-Executable.jar"

# Generate the reference set from all combined approximation sets
# Note that you will need to point this command at the output sets that you generated
# The arguments are " -o (reference set to create) (names of your set files)

echo -n "Generating reference set..."

# java ${JAVA_ARGS} org.moeaframework.util.ReferenceSetMerger -o ${PROBLEM}.reference ./output/Borg_${PROBLEM}_*
# org.moeaframework.analysis.sensitivity.ResultFileMerger

# NOTE: If you want to include extra information (dec vars, etc.) in your reference set, use this command instead:
java ${JAVA_ARGS} PSOResultFileMerger --dimension ${DIMENSION} --epsilon ${EPSILON} --vars ${NVARS} --output yourReferenceSet.set ./data_problem7_*.txt
echo "done."

# Right now this is set up to combine all algorithms together into a single set.