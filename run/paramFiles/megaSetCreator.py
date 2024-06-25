import base64
import random
import sys
import os


def generate_base64_data_points(num_points):
    data_points = []
    for _ in range(num_points):
        random_bytes = random.getrandbits(64).to_bytes(8, byteorder='big')
        base64_string = base64.b64encode(random_bytes).decode('utf-8')
        data_points.append(base64_string)
    return data_points

def create_files(sync_type, set_size, set_difference, additional_strings):
    client_data = generate_base64_data_points(set_size)
    server_data = client_data.copy()
    
    indices_to_change = random.sample(range(set_size), set_difference)
    for index in indices_to_change:
        random_bytes = random.getrandbits(64).to_bytes(8, byteorder='big')
        base64_string = base64.b64encode(random_bytes).decode('utf-8')
        server_data[index] = base64_string
    
    client_filename = f'client_{sync_type}_{set_size}_{set_difference}.cpisync'
    server_filename = f'server_{sync_type}_{set_size}_{set_difference}.cpisync'

    os.environ['CLIENT_FILENAME']=client_filename
    os.environ['SERVER_FILENAME']=server_filename
    os.environ['CSV_FILENAME'] = 'set' + str(sync_type) + '-' + str(set_size) + '-' + str(set_difference)

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
def process_additional_strings(sync_type, set_size, set_difference, additional_strings):
    if(sync_type==13):
        additional_strings[0]="expected: "+str(int(set_size*1.01))

 
def process_params_file(params_file_path):
    with open(params_file_path, 'r') as params_file:
        lines = params_file.readlines()
    with open('paramFiles.txt', 'w') as paramFiles:
        paramFiles.write('')


    sync_type = None
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

