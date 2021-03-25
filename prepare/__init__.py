import random, os, shutil, yaml
import pandas as pd 
import numpy as np
import prepare.utils as utils
import prepare.configs as configs
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket(configs.bucketName)

def run():
    '''
    1. Clean previous dataset (optioonal)
    2. Shuffle availble raw data and split in train - validation
    3. For each raw simulation

    For each raw simulation
        1. Convert Vmems csvs in numpy array + pad to match inputMaxCellsNumber
        2. Encode configs
        3. Save in same folder file called 


    Output:
        runID/compact.csv timestampIdx, Vmem, encoded config

    Output:
        dataset.csv: runID, timestampIdx, Vmem, encoded config
    '''
    raw_folder = "storage/raw/"
    processed_folder = "storage/processed/"
    trainRatio, testRatio, valRatio = 0.7, 0.2, 0.1
    inputMaxCellsNumber = 250
    '''
    runsFolders = []
    for blob in bucket.list_blobs(prefix=raw_folder):
        folderName = blob.name.split("/")
        if (folderName[2] not in runsFolders and folderName[2] != ""):
            runsFolders.append(folderName[2])

    print("Grouping Simulation Data | {} Simulations".format(len(runsFolders)))
    for folderIdx, folderName in enumerate(runsFolders):
        # Keep track of the progress
        if (folderIdx in [int(len(runsFolders)*0.25), int(len(runsFolders)*0.5), int(len(runsFolders)*0.75)]):
            print(">> {} %".format(int(folderIdx / len(runsFolders) * 100)))
        runData = pd.DataFrame()

        print("folderName: " + folderName)
        for blob in bucket.list_blobs(prefix="{}/".format(raw_folder + folderName)):
            print(blob.name)
            if ('csv' in blob.name):
                timestampIdx = blob.name.split("/")[-1].split("_")[1].split(".")[0]
                data = pd.read_csv('gs://{}/{}'.format(configs.bucketName, blob.name))
                data['timestamp'] = timestampIdx 
                data['folderName'] = folderName 
                runData = runData.append(data[['timestamp', 'Vmem [mV]', 'folderName']])

            if ('pkl' in blob.name):
                blob.download_to_filename('/tmp/cells.pkl')
                
                blob = bucket.blob('storage/processed/{}/cells.pkl'.format(folderIdx))
                blob.upload_from_filename('/tmp/cells.pkl')

        runData.columns = ['timestamp', 'vmem', 'folderName']
        runData.to_csv('gs://{}/storage/processed/{}/{}'.format(configs.bucketName, folderIdx, 'simulation.csv'))
        print("")
    '''
    #Split examples in train, test and validation
    runsFolders = []
    for blob in bucket.list_blobs(prefix="storage/processed/"):
        folderName = blob.name.split("/")
        if (folderName[2] not in runsFolders and folderName[2] != ""):
            runsFolders.append(folderName[2])

    random.shuffle(runsFolders)
    trainSet = runsFolders[: int(len(runsFolders) * trainRatio)]
    leftFolders = runsFolders[int(len(runsFolders) * trainRatio) : ]
    testSet = leftFolders[ : int(len(runsFolders) * testRatio)]
    leftFolders = leftFolders[int(len(runsFolders) * testRatio) : ]
    valSet = leftFolders
    
    print("Training Set: {} | Test Set: {} | Validation Set: {}".format(len(trainSet), len(testSet), len(valSet)))

    counters = {
        'train': 0, 
        'test': 0, 
        'validation': 0
    }
    for folders, set_name in zip([trainSet, testSet, valSet], ['train', 'test', 'validation']):
        print("Generating {} Dataset".format(set_name))
        for folderIdx, folderName in enumerate(folders):
            # Keep track of the progress
            if (folderIdx in [int(len(folders)*0.25), int(len(folders)*0.5), int(len(folders)*0.75)]):
                print(">> {} %".format(int(folderIdx / len(folders) * 100)))

            data = pd.read_csv('gs://{}/storage/processed/{}/simulation.csv'.format(configs.bucketName, folderName))

            # Download the file to a destination
            fileDest = '/tmp/rawSimConfig.yml'
            bucket.blob('storage/raw/{}/configs.yml'.format(data['folderName'][0])).download_to_filename(fileDest)
            with open(fileDest, 'r') as stream:
                simConfigRaw = yaml.safe_load(stream)
            simConfigsEncoded = np.asarray(utils.encodeConfigs(simConfigRaw))

            #generate single training examples files
            for timestampIdx in range(data['timestamp'].max() - 1):
                inputVmem = np.asarray(data[data['timestamp'] == timestampIdx]['vmem'])
                outputVmem = np.asarray(data[data['timestamp'] == timestampIdx + 1]['vmem'])

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
                filePath = '/tmp/example.npy'
                np.save(filePath, np.asarray([
                    np.concatenate((inputVmem, simConfigsEncoded), axis=0),
                    outputVmem
                ], dtype="object"))
                if (set_name == "validation"):
                    blob = bucket.blob('dataset/{}/{}/{}.npy'.format(set_name, folderName, timestampIdx))
                else:
                    blob = bucket.blob('dataset/{}/{}.npy'.format(set_name, counters[set_name]))
                blob.upload_from_filename(filePath)

                counters[set_name] += 1
    print("\n>> DONE")
    print("Generated Train {} | Test: {} | Validation {}".format(counters['train'], counters['test'], counters['validation']))
