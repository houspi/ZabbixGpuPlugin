#!/usr/bin/python3
#
# nvidia_gpu_health.py
# Zabbix plugin
# produce NVIDIA GPU helth
# Requirenments: NVidia system tools
#
# 0 - index, 
# 1 - name, 
# 2 - clocks.current.memory [MHz], 
# 3 - utilization.memory [%], 
# 4 - clocks.current.sm [MHz], 
# 5 - utilization.gpu [%], 
# 6 - temperature.gpu, 
# 7 - fan.speed [%], 
# 8 - power.draw [W]


import os
import sys
import subprocess
import re
import socket
import json
import argparse

ProgramDescription = "Print various GPU stat's for the zabbix monitoring system"

KeysDescription='''
index: Index of the selected GPU;\n
name: Name of the selected GPU;\n
clocks.current.memory: Memory Frequency of the selected GPU;\n
utilization.memory: Memory Utilization for the selected GPU;\n
clocks.current.sm: Kernel Frequency for the selected GPU;\n
utilization.gpu:Kernel Utilization for the selected GPU;\n
temperature.gpu: Temperature of the selected GPU;\n
fan.speed: Fan speed in percent for the selected GPU;\n
power.draw: Power consumption in watts for the selected GPU;\n
'''

gpgu_list_param = '-L'
gpu_info_script = "C:\\Program Files\\NVIDIA Corporation\\NVSMI\\nvidia-smi.exe"
gpu_info_params = '--query-gpu=index,gpu_name,clocks.mem,utilization.memory,clocks.sm,utilization.gpu,temperature.gpu,fan.speed,power.draw'
gpu_info_format = '--format=csv'

gpu_info_keys = {
    'index' : 0,
    'name' : 1,
    'clocks.current.memory' : 2,
    'utilization.memory'    : 3,
    'clocks.current.sm'     : 4,
    'utilization.gpu'       : 5,
    'temperature.gpu'       : 6,
    'fan.speed'             : 7,
    'power.draw'            : 8,
    'runnig.time'           : 21,
    'shares.found'          : 22,
    'shares.rejected'       : 23,
    'hash.rate'             : 24,
    'minihg.pool'           : 25,
    'shares.invalid'        : 26,
    'gpu.work'              : 27,
    }

def gpu_stat(gpu_name, key):
    idx = re.search(r'\d+', gpu_name)[0]

    proc = subprocess.Popen([ gpu_info_script, '-i', idx, gpu_info_params, gpu_info_format], 
                                shell=True, stdout=subprocess.PIPE)
    (stdout_data, stderr_data) = proc.communicate()
    if re.search('No device', stdout_data.decode()):
        print('0')
        return 1
    else:
        gpu_info = stdout_data.decode().split('\r\n')[1].split(', ')
        print(gpu_info[gpu_info_keys[key]].split(' ')[0])
        return 0
    return 2

def claymore_stat(gpu_name, key):
    idx = re.search(r'\d+', gpu_name)[0]
    conn = socket.socket()
    conn.connect( ("127.0.0.1", 3333) )
    conn.send(b'{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}\n')
    tmp = conn.recv(2048)
    conn.close()
    responce = json.loads(tmp)
    if( key == 'runnig.time' ) :
        print(responce['result'][1])
        return 0
    elif( key == 'shares.found' ) :
        str = responce['result'][2]
        print(str.split(';')[1])
        return 0
    elif( key == 'shares.rejected' ) :
        str = responce['result'][2]
        print(str.split(';')[2])
        return 0
    elif( key == 'hash.rate' ) :
        str = responce['result'][3]
        print(str.split(';')[int(idx)])
        return 0
    elif( key == 'minihg.pool' ) :
        print(responce['result'][7])
        return 0
    elif( key == 'shares.invalid' ) :
        str = responce['result'][8]
        print(str.split(';')[0])
        return 0
    elif( key == 'gpu.work' ) :
        str = responce['result'][3]
        print(len(str.split(';')))
        return 0
    else :
        return 1
    return 2


def main():

    parser = argparse.ArgumentParser(description=ProgramDescription, add_help=True)
    parser.add_argument("GPU_NAME", help='GPU name. Usually GPU0, GPU2 etc.')
    parser.add_argument("key_name", help=KeysDescription)
    parser.parse_args()

    if not os.path.isfile(gpu_info_script):
        print("0")
        return 2

    gpu_name = sys.argv[1]
    key = sys.argv[2]

    if ( gpu_info_keys[key] <11 ):
        return gpu_stat(gpu_name, key)
    elif ( gpu_info_keys[key] <30 ):
        return claymore_stat(gpu_name, key)
    return 0

if (__name__ == "__main__"):
    exit(main())
