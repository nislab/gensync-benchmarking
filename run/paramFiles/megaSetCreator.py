"""
Author: Nathan Strahs <nstrahs@bu.edu>
Date: Jun 2024

creates server and client .cpisync files to be used in syncs with run_experiments.sh
creates server and client files in the format: CLIENT_SYNCTYPE_SETSIZE_SETDIFFERENCE.cpisync
synctype is the number assigned in gensync code to the algorithm used in the sync

Usage: python3 megaSetCreator.py PARAMS_FILE.txt

Params file is in the format of:
SYNCTYPE
SYNCPARAMS
SET_SIZE SET_DIFFERENCE
SET_SIZE SET_DIFFERENCE
SET_SIZE SET_DIFFERENCE
SYNCTYPE-2
SYNCPARAMS
SET_SIZE SET_DIFFERENCE

EXAMPLE PARAMS.txt:
13 #bloomFilter
expected: 10000 #does not matter, program will edit this
eltSize: 12
falsePosProb: 0.01
1000 10
1000 20
2000 10
14 #MET_IBLT sync
eltSize: 12
10000 200
10000 300
"""

import base64
import random
import sys
import os

#generates base 64 data points to be used
def generate_base64_data_points(num_points):
    data_points = []
    for _ in range(num_points):
        random_bytes = random.getrandbits(64).to_bytes(8, byteorder='big')
        base64_string = base64.b64encode(random_bytes).decode('utf-8')
        data_points.append(base64_string)
    return data_points

#creates and properly names the files
def create_files(sync_type, set_size, set_difference, additional_strings):
    client_data = generate_base64_data_points(set_size)
    server_data = client_data.copy()

    #changes random data points according to the set difference provided
    indices_to_change = random.sample(range(set_size), set_difference)
    for index in indices_to_change:
        random_bytes = random.getrandbits(64).to_bytes(8, byteorder='big')
        base64_string = base64.b64encode(random_bytes).decode('utf-8')
        server_data[index] = base64_string

    #names the .cpisync files in a format to be run by runMega_experiments.sh
    client_filename = f'client_{sync_type}_{set_size}_{set_difference}.cpisync'
    server_filename = f'server_{sync_type}_{set_size}_{set_difference}.cpisync'

    os.environ['CLIENT_FILENAME']=client_filename
    os.environ['SERVER_FILENAME']=server_filename
    os.environ['CSV_FILENAME'] = 'set' + str(sync_type) + '-' + str(set_size) + '-' + str(set_difference)

    #formats the paramsFile to be passed to the runMegaExperiments
    with open('paramFiles.txt', 'a') as paramFiles:
        paramFiles.write(server_filename + ' ' + client_filename + ' set' + str(sync_type) + '-' + str(set_size) + '-' + str(set_difference) + '\n')

    with open(client_filename, 'w') as client_file:
        client_file.write('Sync protocol (as in GenSync.h): ' + str(sync_type) + '\n')
        client_file.write('\n'.join(additional_strings) + '\n')
        client_file.write('Sketches\n')
        client_file.write('--------------------------------------------------------------------------------\n')
        client_file.write('\n'.join(client_data))

    with open(server_filename, 'w') as server_file:
        server_file.write('Sync protocol (as in GenSync.h): ' + str(sync_type) + '\n')
        server_file.write('\n'.join(additional_strings) + '\n')
        server_file.write('Sketches\n')
        server_file.write('--------------------------------------------------------------------------------\n')
        server_file.write('\n'.join(server_data))

#adjusts .cpisync files for specific sync types
def process_additional_strings(sync_type, set_size, set_difference, additional_strings):
    if(sync_type==13):
        additional_strings[0]="expected: "+str(int(set_size*1.01))

#processes param files passed to the program
def process_params_file(params_file_path):
    with open(params_file_path, 'r') as params_file:
        lines = params_file.readlines()
    with open('paramFiles.txt', 'w') as paramFiles:
        paramFiles.write('')


    sync_type = None
    #variable takes care of the params
    additional_strings = []
    is_collecting_strings = False
    
    for line in lines:
        line = line.strip()
        if line.isdigit():
            if sync_type is not None and additional_strings:
                additional_strings = []  # Reset additional_strings for the next syncType
            
            sync_type = int(line)
            is_collecting_strings = True
        else:
            parts = line.split()
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                set_size = int(parts[0])
                set_difference = int(parts[1])
                process_additional_strings(sync_type, set_size, set_difference, additional_strings)
                create_files(sync_type, set_size, set_difference, additional_strings)
            elif is_collecting_strings:
                additional_strings.append(line)
    
    return sync_type

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python megaSetCreater.py <params_file_path>")
        sys.exit(1)
    
    params_file_path = sys.argv[1]
    sync_type = process_params_file(params_file_path)
    
    print("Last syncType processed:", sync_type)

