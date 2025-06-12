#!/bin/bash
PBBS_BENCHMARKS_DIR="/mnt/sda4/pbbsbench/benchmarks"

dir_arr=("minSpanningForest/parallelFilterKruskal" "maximalMatching/incrementalMatching" "maximalIndependentSet/incrementalMIS" "spanningForest/ndST" "breadthFirstSearch/backForwardBFS" "integerSort/parallelRadixSort" "comparisonSort/sampleSort" "removeDuplicates/parlayhash" "histogram/parallel" "nearestNeighbors/octTree" "rayCast/kdTree" "convexHull/quickHull" "delaunayTriangulation/incrementalDelaunay" "delaunayRefine/incrementalRefine" "rangeQuery2d/parallelPlaneSweep" "wordCounts/histogram" "invertedIndex/parallel" "suffixArray/parallelRange" "longestRepeatedSubstring/doubling" "comparisonSort/quickSort" "comparisonSort/mergeSort" "comparisonSort/stableSampleSort" "comparisonSort/ips4o" "removeDuplicates/serial_sort" "suffixArray/parallelKS" "spanningForest/incrementalST" "breadthFirstSearch/simpleBFS" "breadthFirstSearch/deterministicBFS")

for name in ${dir_arr[@]}; do
  #echo $name;
  cp $PBBS_BENCHMARKS_DIR/$name/testInputs $PBBS_BENCHMARKS_DIR/$name/genData;
  sed -i 's/runTests.timeAllArgs(bnchmrk, benchmark, checkProgram, dataDir, tests)/runTests.genAllData(tests, dataDir)/' $PBBS_BENCHMARKS_DIR/$name/genData;
done

echo "Generating data ..."

cd $PBBS_BENCHMARKS_DIR/minSpanningForest/parallelFilterKruskal; ./genData
cd $PBBS_BENCHMARKS_DIR/maximalMatching/incrementalMatching; ./genData
cd $PBBS_BENCHMARKS_DIR/maximalIndependentSet/incrementalMIS; ./genData
cd $PBBS_BENCHMARKS_DIR/spanningForest/ndST; ./genData
cd $PBBS_BENCHMARKS_DIR/breadthFirstSearch/backForwardBFS; ./genData
cd $PBBS_BENCHMARKS_DIR/integerSort/parallelRadixSort; ./genData
cd $PBBS_BENCHMARKS_DIR/comparisonSort/sampleSort; ./genData
cd $PBBS_BENCHMARKS_DIR/removeDuplicates/parlayhash; ./genData
cd $PBBS_BENCHMARKS_DIR/histogram/parallel; ./genData
cd $PBBS_BENCHMARKS_DIR/nearestNeighbors/octTree; ./genData
cd $PBBS_BENCHMARKS_DIR/rayCast/kdTree; ./genData
cd $PBBS_BENCHMARKS_DIR/convexHull/quickHull; ./genData
cd $PBBS_BENCHMARKS_DIR/delaunayTriangulation/incrementalDelaunay; ./genData
cd $PBBS_BENCHMARKS_DIR/delaunayRefine/incrementalRefine; ./genData
cd $PBBS_BENCHMARKS_DIR/rangeQuery2d/parallelPlaneSweep; ./genData
cd $PBBS_BENCHMARKS_DIR/wordCounts/histogram; ./genData
cd $PBBS_BENCHMARKS_DIR/invertedIndex/parallel; ./genData
cd $PBBS_BENCHMARKS_DIR/suffixArray/parallelRange; ./genData
cd $PBBS_BENCHMARKS_DIR/longestRepeatedSubstring/doubling; ./genData

cd $PBBS_BENCHMARKS_DIR/comparisonSort/quickSort; ./genData
cd $PBBS_BENCHMARKS_DIR/comparisonSort/mergeSort; ./genData
cd $PBBS_BENCHMARKS_DIR/comparisonSort/stableSampleSort; ./genData
cd $PBBS_BENCHMARKS_DIR/comparisonSort/ips4o; ./genData
cd $PBBS_BENCHMARKS_DIR/removeDuplicates/serial_sort; ./genData
cd $PBBS_BENCHMARKS_DIR/suffixArray/parallelKS; ./genData
cd $PBBS_BENCHMARKS_DIR/spanningForest/incrementalST; ./genData
cd $PBBS_BENCHMARKS_DIR/breadthFirstSearch/simpleBFS; ./genData
cd $PBBS_BENCHMARKS_DIR/breadthFirstSearch/deterministicBFS; ./genData
