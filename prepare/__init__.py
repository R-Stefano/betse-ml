import random, os, shutil, yaml, gzip
import pandas as pd 
import numpy as np
import prepare.utils as utils
import prepare.configs as configs
from google.cloud import storage
import pickle

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

    processFiles = False
    generateDataset = True
    splitDataset = True

    if (processFiles):
        runsFoldersProcessed = []
        for blob in bucket.list_blobs(prefix=processed_folder):
            folderName = blob.name.split("/")
            if (folderName[2] not in runsFoldersProcessed and folderName[2] != ""):
                runsFoldersProcessed.append(folderName[2])
        print("Grouping Simulation Data | Runs Already Processed {}".format(len(runsFoldersProcessed)))
        
        runsFolders = []
        for blob in bucket.list_blobs(prefix=raw_folder):
            folderName = blob.name.split("/")
            if (folderName[2] not in runsFolders and folderName[2] != "" and folderName[2] not in runsFoldersProcessed):
                runsFolders.append(folderName[2])

        print("Grouping Simulation Data | Runs to Process {}".format(len(runsFolders)))
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

            runData.columns = ['timestamp', 'vmem', 'folderName']
            runData.to_csv('gs://{}/storage/processed/{}/{}'.format(configs.bucketName, folderIdx, 'simulation.csv'))
            print("")

    if (generateDataset):
        utils.generateDataset()

    if (splitDataset):
        trainRatio, testRatio, valRatio = 0.7, 0.2, 0.1

        runsIdxs = []
        for blob in bucket.list_blobs(prefix="storage/ready/"):
            folderName = blob.name.split("/")
            if (folderName[2] not in runsIdxs and folderName[2] != ""):
                runsIdxs.append(folderName[2])

        #Split examples in train, test and validation
        random.seed(1)
        random.shuffle(runsIdxs)
        trainSet = runsIdxs[: int(len(runsIdxs) * trainRatio)]
        leftFolders = runsIdxs[int(len(runsIdxs) * trainRatio) : ]
        testSet = leftFolders[ : int(len(runsIdxs) * testRatio)]
        leftFolders = leftFolders[int(len(runsIdxs) * testRatio) : ]
        valSet = leftFolders
        
        print("Training Set: {} | Test Set: {} | Validation Set: {}".format(len(trainSet), len(testSet), len(valSet)))

        counters = {
            'train': 0, 
            'test': 0, 
            'validation': 0
        }
        for folders, set_name in zip([trainSet, testSet, valSet], ['train', 'test', 'validation']):
            print("Generating {} Dataset".format(set_name))
            for i, runIdx in enumerate(folders):
                print('({}/{})'.format(i, len(folders)))
                for blob in bucket.list_blobs(prefix="storage/ready/{}/".format(runIdx)):
                    bucket.copy_blob(blob, bucket, 'dataset/{}/{}.npy'.format(set_name, counters[set_name]))
                    counters[set_name] += 1

        print("\n>> DONE")
        print("Generated Train {} | Test: {} | Validation {}".format(counters['train'], counters['test'], counters['validation']))

def analyze():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_theme()

    destFolder = "/tmp/betse-dataset"
    if (not os.path.exists(destFolder)):
        os.makedirs(destFolder)

    dataset = pd.DataFrame()
    for idx, blob in enumerate(bucket.list_blobs(prefix="dataset/train/")):
        fileName = blob.name.split("/")[2]
        print(fileName)
        bucket.blob(blob.name).download_to_filename(destFolder + "/" + fileName)
        x, configs, y = np.load(destFolder + "/" + fileName, allow_pickle = True)
        data = pd.DataFrame({
            'ID': [fileName.split(".")[0] for _ in range(len(x))],
            'inputVmem': x[:, 0],
            'targetVmem': y,
            'deltaVmem': (np.abs(x[:, 0]) - np.abs(y)),
            'input_Dm_Na': x[:, 1],
            'input_Dm_K': x[:, 2],
            'input_Dm_Cl': x[:, 3],
            'input_Dm_Ca': x[:, 4],
        })
        dataset = dataset.append(data)
        if (idx == 20):
            break
    print(dataset.head())
    print(len(dataset))

    # Distribution in Vmem Values
    #sns_plot = sns.jointplot(x="inputVmem", y="targetVmem", data=dataset, height=10, aspect=2, kind="kde")
    #plt.show()

    # Distribution in Vmem Changes
    #sns.displot(dataset, x="deltaVmem", kind="kde", height=10, aspect=2,)
    #plt.show()

    # Distribution in Diffusion Constanrt vs Mode Vmem
    sns_plot = sns.jointplot(x="input_Dm_Na", y="targetVmem", data=dataset, height=10, aspect=2, kind="kde")
    plt.show()