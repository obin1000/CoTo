#!/bin/bash

nsys_host_location="/opt/nvidia/nsight-systems/2023.4.4/host-linux-x64/"
nsys_report=./nvcomp_lz4_nsys_results_2024-03-19-121204.nsys-rep
output_file="nsys_flamegraph_`date +%F-%H%M%S"

python $nsys_host_location/Scripts/Flamegraph/stackcollapse_nsys.py $nsys_report | ./flamegraph.pl > ${output_file}.svg

