#!/bin/bash

prefix="aus-domain-urls_"
script_command="python3 __init__.py"

mkdir -p ./data/completed

for path in data/*;
do
	line=`basename $path`
	echo $line
	if [[ $line == $prefix* ]]; then
		echo "Starting seeds in $line"
		output=$($script_command data/$line 2>&1 >/dev/null)
		status=$?
		if [ $status != 0 ]; then
		    	echo "Something went wrong in $line. Error code: $status"
			echo "$output" > "./data/completed/error_$line"
		else
			echo "Seeds in $line have been crawled successfully."
		fi
		mv "data/$line"  data/completed
	fi
done

