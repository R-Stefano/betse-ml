import random, os, shutil, yaml, gzip
import pandas as pd 
import numpy as np
import prepare.configs as configs
from google.cloud import storage
import pickle
import time

storage_client = storage.Client()
bucket = storage_client.bucket(configs.bucketName)

def encodeConfigs(_confs):
    return [
        _confs['sim time settings']['time step'],
        _confs['sim time settings']['total time'],
        _confs['sim time settings']['sampling rate'],
        int(_confs['change Na mem']['event happens']),
        _confs['change Na mem']['change start'],
        _confs['change Na mem']['change finish'],
        _confs['change Na mem']['change rate'],
        _confs['change Na mem']['multiplier'],
        int(_confs['change K mem']['event happens']),
        _confs['change K mem']['change start'],
        _confs['change K mem']['change finish'],
        _confs['change K mem']['change rate'],
        _confs['change K mem']['multiplier']
    ]


def generateDataset():
    srcFolder = "storage/processed"
    destFolder = "storage/ready"
    inputMaxCellsNumber = 250
    retryCounter = 0

    # Fetch available simulation folders
    runsIdxs = []
    for blob in bucket.list_blobs(prefix=srcFolder):
        folderName = blob.name.split("/")
        if (folderName[2] not in runsIdxs and folderName[2] != ""):
            runsIdxs.append(folderName[2])

    # Ftech simulation folders already processed
    with open("./prepare/processed.txt","r") as f:
        processedRunsIdxs = f.readlines()
        processedRunsIdxs = [folder.strip() for folder in processedRunsIdxs]

    availableFolders = []
    for runIdx in runsIdxs:
        if (runIdx not in processedRunsIdxs):
            availableFolders.append(runIdx)

    print("[GENERATE DATASET] Folders {} | Processed {} | Left {}".format(len(runsIdxs), len(processedRunsIdxs), len(availableFolders)))
    for i, runFolderIdx in enumerate(availableFolders):
        # Keep track of the progress
        if (i in [int(len(availableFolders)*0.25), int(len(availableFolders)*0.5), int(len(availableFolders)*0.75)]):
            print(">> {} %".format(int(i / len(availableFolders) * 100)))

        try:
            data = pd.read_csv('gs://{}/{}/{}/simulation.csv'.format(configs.bucketName, srcFolder, runFolderIdx))
            print(">> {} | {}".format(runFolderIdx, data['folderName'][0]))

            # 1. Download Sim Config File and encode It
            fileDest = '/tmp/rawSimConfig.yml'
            bucket.blob('storage/raw/{}/configs.yml'.format(data['folderName'][0])).download_to_filename(fileDest)
            with open(fileDest, 'r') as stream:
                simConfigRaw = yaml.safe_load(stream)
            simConfigsEncoded = np.asarray(encodeConfigs(simConfigRaw))
            simConfigsEncoded = np.append(simConfigsEncoded, [0]) # Add timestamp information

            # 2. Download Sim.betse File and open it ( to extract Membrane permeabilities values)
            fileDest = '/tmp/sim_1.betse.gz'
            bucket.blob('storage/raw/{}/sim_1.betse.gz'.format(data['folderName'][0])).download_to_filename(fileDest)
            with gzip.open(fileDest, "rb") as f:
                sim, cells, params = pickle.load(f)

            # 3. Generate training examples files. One for each simulation timestep using sim config, sim.betse & vmems
            for timestampIdx in range(len(sim.time)):
                inputVmem = np.asarray(data[data['timestamp'] == timestampIdx]['vmem'])
                outputVmem = np.asarray(data[data['timestamp'] == timestampIdx + 1]['vmem'])

                # Update timestamp information
                simConfigsEncoded[simConfigsEncoded.shape[0] - 1] = timestampIdx

                # 1. Compute cells perms values from cells membranes perms values. From {3, 6} values to 1 (average)
                cellsPopulationSize = inputVmem.shape[0]
                cells_mems = [[] for cell in range(cellsPopulationSize)]
                for memUniqueIdx, cellIdx in enumerate(cells.mem_to_cells):
                    cells_mems[cellIdx].append(sim.dd_time[timestampIdx][:, memUniqueIdx])

                cells_permeabilities = []
                for cellMembranes in cells_mems:
                    cells_permeabilities.append(np.mean(cellMembranes, axis=0))
                cells_permeabilities = np.asarray(cells_permeabilities) # N, 4 # K, Na, M-, Proteins-

                # concat Vmem values with perms values
                inputVmem = np.concatenate((inputVmem.reshape((-1, 1)), cells_permeabilities), axis=1) # N, 5

                # concat cells centers to input vector
                inputVmem = np.concatenate((inputVmem, cells.cell_centres), axis=1) # N, 7

                # Concat env concentrations
                env_cc = np.transpose(sim.cc_env_time[timestampIdx])[ : inputVmem.shape[0]] # get only same shape as inputVmem since env cc all the same
                inputVmem = np.concatenate((inputVmem, env_cc), axis=1) # N, 11

                # Concat cytosilic concentrations
                cytosolic_cc = np.transpose(sim.cc_time[timestampIdx])
                inputVmem = np.concatenate((inputVmem, cytosolic_cc), axis=1) # N, 15

                #Pad Input
                '''
                TODO:
                - Not pad with 0 since it is a possible Vmem value.
                '''
                if (inputVmem.shape[0] < inputMaxCellsNumber):
                    inputVmemPad = np.zeros((inputMaxCellsNumber, inputVmem.shape[1]))
                    inputVmemPad[:inputVmem.shape[0]] = inputVmem
                    inputVmem = inputVmemPad

                    outputVmemPad = np.zeros((inputMaxCellsNumber))
                    outputVmemPad[:outputVmem.shape[0]] = outputVmem
                    outputVmem = outputVmemPad
                #Discard Input
                elif (inputVmem.shape[0] > inputMaxCellsNumber):
                    print("<<ATTENTION>> Found Input with Numbers of cells higher that current Max: {} > {}".format(inputVmem.shape[0], inputMaxCellsNumber))
                    continue
                
                # Discard example if data
                # - Vmem < - 100 || > 100
                # - K_env, Na_env, M_env, X_env, K_cc, Na_cc, M_cc, X_cc > 1000
                #

                if (np.any(inputVmem[:, 0] < -100) or np.any(inputVmem[:, 0] > 100)):
                    print("Discard example, Vmem {}".format(np.max(np.abs(inputVmem))))
                    continue

                if (np.any(inputVmem[: , 7:] > 1000)):
                    print("Discard example, Concentration {}".format(np.max(inputVmem[: , 7:])))
                    continue

                if (np.any(outputVmem[:, 0] < -100) or np.any(outputVmem[:, 0] > 100)):
                    print("Discard example, Vmem Output {}".format(np.max(np.abs(outputVmem))))
                    continue
                #print("inputVmem length: {}".format(inputVmem.shape[0]))
                #print("Configs length: {}".format(configs.shape[0]))
                #print("outputVmem length: {}".format(outputVmem.shape[0]))
                filePath = '/tmp/example.npy'
                np.save(filePath, np.asarray([
                    inputVmem,
                    simConfigsEncoded,
                    outputVmem
                ], dtype="object"))
                blob = bucket.blob('{}/{}/{}.npy'.format(destFolder, runFolderIdx, timestampIdx))
                blob.upload_from_filename(filePath)

            retryCounter = 0
            with open("./prepare/processed.txt","a+") as f:
                f.write(runFolderIdx + "\n")
        # If for some reason processing fails. Handle it. It will not save on the processed.txt allowing to be processed at the next restart
        except:
            print("Handle Excpetion | Sleeping for {}".format(2 ** retryCounter))
            time.sleep(2 ** retryCounter) # sleep since may be due to too many requests
            retryCounter += 1
            continue