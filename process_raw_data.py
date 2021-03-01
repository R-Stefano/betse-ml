import os
import shutil
import numpy as np
import pandas as pd 
import yaml
import sys
import random
random.seed(0)

raw_folder = "data/raw/"
processed_folder = "data/processed/"
inputMaxCellsNumber = 250
trainingSetSize = 0.7

if (True):#confirm("Do you want to clean the folder?")):
    print("Cleaning Folder")
    shutil.rmtree(processed_folder)
    os.makedirs(processed_folder)
    os.makedirs(processed_folder + "train/")
    os.makedirs(processed_folder + "validation/")

def encodeConfigs(configs):
    _timestep = configs['sim time settings']['time step']
    _simtime = configs['sim time settings']['total time']
    _temp_event = int(configs['change temperature']['event happens']) #convert True or False to 1 or 0
    _temp_event_start = configs['change temperature']['change start']
    _temp_event_finish = configs['change temperature']['change finish']
    _temp_event_change_rate = configs['change temperature']['change rate']
    _temp_event_change_multiplier = configs['change temperature']['multiplier']
    _Na_env_event = int(configs['change Na env']['event happens']) #convert True or False to 1 or 0
    _Na_env_event_start = configs['change Na env']['change start']
    _Na_env_event_finish = configs['change Na env']['change finish']
    _Na_env_event_change_rate = configs['change Na env']['change rate']
    _Na_env_event_change_multiplier = configs['change Na env']['multiplier']
    _K_env_event = int(configs['change K env']['event happens']) #convert True or False to 1 or 0
    _K_env_event_start = configs['change K env']['change start']
    _K_env_event_finish = configs['change K env']['change finish']
    _K_env_event_change_rate = configs['change K env']['change rate']
    _K_env_event_change_multiplier = configs['change K env']['multiplier']
    _block_gj_event = int(configs['block gap junctions']['event happens']) #convert True or False to 1 or 0
    _block_gj_event_start = configs['block gap junctions']['change start']
    _block_gj_event_finish = configs['block gap junctions']['change finish']
    _block_gj_event_change_rate = configs['block gap junctions']['change rate']
    _block_gj_event_change_multiplier = configs['block gap junctions']['random fraction']
    _block_NaKATP_pump_event = int(configs['block NaKATP pump']['event happens']) #convert True or False to 1 or 0
    _block_NaKATP_pump_event_start = configs['block NaKATP pump']['change start']
    _block_NaKATP_pump_event_finish = configs['block NaKATP pump']['change finish']
    _block_NaKATP_pump_event_change_rate = configs['block NaKATP pump']['change rate']

    return [
        _timestep,
        _simtime,
        _temp_event,
        _temp_event_start,
        _temp_event_finish,
        _temp_event_change_rate,
        _temp_event_change_multiplier,
        _Na_env_event,
        _Na_env_event_start,
        _Na_env_event_finish,
        _Na_env_event_change_rate,
        _Na_env_event_change_multiplier,
        _K_env_event,
        _K_env_event_start,
        _K_env_event_finish,
        _K_env_event_change_rate,
        _K_env_event_change_multiplier,
        _block_gj_event,
        _block_gj_event_start,
        _block_gj_event_finish,
        _block_gj_event_change_rate,
        _block_gj_event_change_multiplier,
        _block_NaKATP_pump_event,
        _block_NaKATP_pump_event_start,
        _block_NaKATP_pump_event_finish,
        _block_NaKATP_pump_event_change_rate
    ]

dataset = os.listdir(raw_folder)
random.shuffle(dataset)

training_set = dataset[ : int(len(dataset) * trainingSetSize)]
validation_set = dataset[int(len(dataset) * trainingSetSize) : ]


for filenames, set_name in zip([training_set, validation_set], ['train', 'validation']):
    for idx, folder in enumerate(filenames):
        example = []

        try:
            inputVmem = pd.read_csv(raw_folder + folder + "/Vmem2D_0.csv")
            outputVmem = pd.read_csv(raw_folder + folder + "/Vmem2D_1.csv")
            with open(raw_folder + folder + '/configs.yml', 'r') as stream:
                configs = yaml.safe_load(stream)
        except FileNotFoundError:
            continue
        except:
            print(sys.exc_info()[0])
            continue


        inputVmem = np.asarray(inputVmem['Vmem [mV]'])
        outputVmem = np.asarray(outputVmem['Vmem [mV]'])
        configs = np.asarray(encodeConfigs(configs))


        #Pad Input
        if (inputVmem.shape[0] < inputMaxCellsNumber):

            inputVmemPad = np.zeros((inputMaxCellsNumber))
            inputVmemPad[:inputVmem.shape[0]] = inputVmem
            inputVmem = inputVmemPad

            outputVmemPad = np.zeros((inputMaxCellsNumber))
            outputVmemPad[:outputVmem.shape[0]] = outputVmem
            outputVmem = outputVmemPad
        #Discard Input
        elif (inputVmem.shape[0] > inputMaxCellsNumber):
            print("<<ATTENTION>> Found Input with Numbers of cells higher that current Max: {} > {}".format(inputVmem.shape[0], inputMaxCellsNumber))
            continue


        #print("inputVmem length: {}".format(inputVmem.shape[0]))
        #print("Configs length: {}".format(configs.shape[0]))
        #print("outputVmem length: {}".format(outputVmem.shape[0]))
        example.append(np.concatenate((inputVmem, configs), axis=0))
        example.append(outputVmem)

        np.save(processed_folder + set_name + '/id_{}.npy'.format(idx) , example)
