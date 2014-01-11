#!/usr/bin/env bash

# bash wrapper script for sim.py.

result=`./sim.py $*`
err=$?

if [ ${err} == 0 ]
then
	# Write output in proper format
	# http://memshub.org/site/memosa_docs/puq/reference/puqutil.html
	echo "HDF5:{'name': 'z', 'desc': 'Output of the quadratic.', 'value': ${result}}:5FDH"
else
	exit ${err}
fi
