#!/bin/bash

prefix="aus-domain-urls_"
script_command="python3 harvest.py"

mkdir -p ./data/completed

for path in data/*;
do
	line=`basename $path`
	echo $line
	if [[ $line == $prefix* ]]; then
		echo "Starting seeds in $line"
		$script_command data/$line 2>"./errors/error_$line"
		status=$?
		if [ $status != 0 ]; then
		    	echo "Something went wrong in $line. Error code: $status"
			cat  "./data/completed/error_$line"
		else
			echo "Seeds in $line have been crawled successfully."
		fi
		mv "data/$line"  data/completed
	fi
done

