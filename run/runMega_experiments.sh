#!/bin/bash -x


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

# Read the file line by line
#while IFS= read -r line
while IFS= read -r line || [[ -n "$line" ]]; do
  (
  echo $line
  read -r serverFile clientFile csvFileName <<< "$line"
   
  # Print the variables for debugging purposes and set as enviornment variables
  echo "Server File: $serverFile"
  echo "Client File: $clientFile"
  echo "CSV File Name: $csvFileName"

  OUTPUT_FILE="server_client_names.txt"
  echo "${serverFile} ${clientFile} ${csvFileName}" > ${OUTPUT_FILE}

  export CSV_FILENAME=$csvFileName
  export CLIENT_FILENAME=$clientFile
  export SERVER_FILENAME=$serverFile
  echo "Running run_experiments.sh"
  ./run_experiments.sh -r "128.197.128.230:/home/nathanstrahs/EXPERIMENTS/MEGA-EXPERIMENTS/$CSV_FILENAME" &
  first_script_pid=$!
  
  # Set a timeout for 1 minutes (60 seconds)
  timeout=60
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
  
  ./run_experiments.sh -p "128.197.128.230:/home/nathanstrahs/EXPERIMENTS/MEGA-EXPERIMENTS/$CSV_FILENAME" &
  second_script_pid=$!
  wait $second_script_pid
  

  rm $OUTPUT_FILE
  echo "Pulled the CSV"
  )
done < "$paramFile"

