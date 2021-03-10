import random, os, shutil, yaml
import pandas as pd 
import numpy as np
import prepare.utils as utils

def run():
    '''
    1. Clean previous dataset (optioonal)
    2. Shuffle availble raw data and split in train - validation
    3. For each raw simulation

    For each raw simulation
        1. Reject example if simulation failed
        2. Convert Vmems csvs in numpy array + pad to match inputMaxCellsNumber
        3. Encode configs
        4. Save

    '''
    processed_folder = "storage/processed/"
    raw_folder = "storage/raw/"
    trainingSetSize = 0.7
    inputMaxCellsNumber = 250

    if (True):#confirm("Do you want to clean the folder?")):
        print("Cleaning Old Dataset..")
        shutil.rmtree(processed_folder)
        os.makedirs(processed_folder)
        os.makedirs(processed_folder + "train/")
        os.makedirs(processed_folder + "validation/")

    dataset = os.listdir(raw_folder)
    random.shuffle(dataset)

    training_set = dataset[ : int(len(dataset) * trainingSetSize)]
    validation_set = dataset[int(len(dataset) * trainingSetSize) : ]

    for filenames, set_name in zip([training_set, validation_set], ['train', 'validation']):
        print("Generating {} Dataset".format(set_name))
        for idx, folder in enumerate(filenames):
            # Keep track of the progress
            if (idx in [int(len(filenames)*0.25), int(len(filenames)*0.5), int(len(filenames)*0.75)]):
                print(">> {} %".format(int(idx / len(filenames) * 100)))

            example = []

            # Exclude simulation data if simulation failed because incomplete (missing Vmem2D_1.csv)
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
            configs = np.asarray(utils.encodeConfigs(configs))

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

            np.save(processed_folder + set_name + '/id_{}.npy'.format(folder) , example)

    print("\n>> DONE")
    print(" Raw Data: {} | Train Ratio {}".format(len(dataset), trainingSetSize))
    print("Generated: {} | Train {} | Val: {}".format(len(os.listdir(processed_folder + "train/")) + len(os.listdir(processed_folder + "validation/")), len(os.listdir(processed_folder + "train/")), len(os.listdir(processed_folder + "validation/"))))
