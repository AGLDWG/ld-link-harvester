#!/bin/bash

prefix="aus-domain-urls_"
script_command="python3 dummy_run.py"

mkdir -p ./data/completed

for line in $(ls data);
do
	if [[ $line == $prefix* ]]; then
		echo "Starting seeds in $line"
		output=$($script_command $line 2>&1 >/dev/null)
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

