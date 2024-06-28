#!/bin/bash

# Author: Nathan Strahs <nstrahs@bu.edu>
# Date: Jun 2024
#
# USAGE: ./runMega_experiments.sh PARAM_FILE.txt
#
# PARAMFILE.txt is to be used in combination with megaSetCreator.py
# PARAMFILE.txt contains all the necessary filenames for the syncs to be conducted


# Check if the correct number of arguments are provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 paramFiles.txt"
  exit 1
fi

paramFile=$1

# Check if the file exists
if [ ! -f "$paramFile" ]; then
  echo "File not found!"
  exit 1
fi

#create a list of syncs to be conducted from the paramFile
mapfile -t lines < "$paramFile"

for line in "${lines[@]}"; do
(
# Read the file line by line and extract filenames
  echo $line
  read -r serverFile clientFile csvFileName <<< "$line"

  #create a file to be sent to the shell running the experiments
  OUTPUT_FILE="server_client_names.txt"
  echo "${serverFile} ${clientFile} ${csvFileName}" > ${OUTPUT_FILE}

  export CSV_FILENAME=$csvFileName
  export CLIENT_FILENAME=$clientFile
  export SERVER_FILENAME=$serverFile

  #run the experiments on the remote
  echo "Running run_experiments.sh"
  ./run_experiments.sh -r "128.197.128.230:/home/nathanstrahs/EXPERIMENTS/MEGA-EXPERIMENTS/$CSV_FILENAME" &
  first_script_pid=$!

  # Set a timeout
  timeout=700
  while [ $timeout -gt 0 ]; do
    sleep 1
    if ! ps -p $first_script_pid > /dev/null; then
      break
    fi
    timeout=$((timeout-1))
  done

  if ps -p $first_script_pid > /dev/null; then
    # If the first script is still running after timeout, kill it
    echo "First script timed out, killing it..."
    kill $first_script_pid
    wait $first_script_pid 2>/dev/null
  fi

  #pull the csv of the experiments
  ./run_experiments.sh -p "128.197.128.230:/home/nathanstrahs/EXPERIMENTS/MEGA-EXPERIMENTS/$CSV_FILENAME"
  sleep 2

  rm $OUTPUT_FILE
  echo "Pulled the CSV, moving to next params"
  )
done < "$paramFile"
