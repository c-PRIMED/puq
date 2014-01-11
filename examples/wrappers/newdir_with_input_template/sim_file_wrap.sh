#!/usr/bin/env bash

# bash wrapper script for sim_file.py.

echo a=$1 > input.txt
echo b=$2 >> input.txt
echo c=$3 >> input.txt
echo x=$4 >> input.txt


`../sim_file.py input.txt`
err=$?

if [ ${err} == 0 ]
then
	# Write output in proper format
	# http://memshub.org/site/memosa_docs/puq/reference/puqutil.html
	out=`cat output.txt`
	out=${out%.}
	# Remove first 14 chars.  length("The answer is ")
	out=${out:14}
	echo "HDF5:{'name': 'z', 'desc': 'Output of the quadratic.', 'value': ${out}}:5FDH"
else
	exit ${err}
fi
