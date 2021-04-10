import random, os, shutil, yaml, gzip
import pandas as pd 
import numpy as np
import prepare.utils as utils
import prepare.configs as configs
from google.cloud import storage
import pickle
from scipy import interpolate as interp

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

            fileDest = '/tmp/sim_1.betse.gz'
            bucket.blob('storage/raw/{}/sim_1.betse.gz'.format(data['folderName'][0])).download_to_filename(fileDest)
            with gzip.open(fileDest, "rb") as f:
                sim, cells, params = pickle.load(f)

            '''
            print(cells.map_ij2k[:50])
            print(cells.index_k)
            break
            # Generate full grid
            xv = np.linspace(cells.xmin, cells.xmax, params.plot_grid_size)
            yv = np.linspace(cells.xmin, cells.xmax, params.plot_grid_size)
            envXGrid, envYGrid = np.meshgrid(xv,yv) # (50, 50), (50, 50)

            print(cells.cell_i)
            result = interp.griddata(
                (cells.cell_centres[:, 0], cells.cell_centres[:, 1]),
                cells.cell_i, 
                (envXGrid, envYGrid),
                method='linear', fill_value=0)

            resultInt = result.astype(int)

            cellsIdxs = resultInt[resultInt > 0]
            print(np.sort(cellsIdxs.reshape(-1)))
            from matplotlib import pyplot as plt
            plt.imshow((resultInt), interpolation='nearest')
            plt.show()

            break
            print(params.nx, params.ny, params.d_cell, params.ac)
            print(cells.xyaxis)
            #############################àXcoords = 
            #############################àYcoords = 
            #print(cells.clust_xy.shape) (392, 2)
            ####print(cells.mesh.shape)
            #print(cells.cell_sa.shape) #(225,)
            #print(cells.nn_i.shape) #(1294,)
            #print(cells.cell_nn_i.shape) #(1294, 2)
            #print(cells.grid_len) # 625
            #print(cells.Xgrid.shape) # (50, 50)
            #print(cells.Ygrid.shape) # (50, 50)
            print(cells.grid_obj.cents_X) # 25, 25
            print(cells.grid_obj.xy_cents.shape)


            print(cells.grid_obj.__dict__.keys())
            for key in cells.__dict__:
                print(key)
            ##########print(cells.mesh.image_mask.__dict__.keys())
            #print(cells.mesh.vor_cell_i.shape)
            #print(cells.mesh.vor_cell_i[:5])
            #print(cells.mesh.xyaxis)

            break
            '''
            #generate single training examples files
            for timestampIdx in range(data['timestamp'].max()):
                inputVmem = np.asarray(data[data['timestamp'] == timestampIdx]['vmem'])
                outputVmem = np.asarray(data[data['timestamp'] == timestampIdx + 1]['vmem'])
                cellsPopulationSize = inputVmem.shape[0]

                #Compute cells perms values from cells membranes perms values. From {3, 6} values to 1 (average)
                cells_mems = [[] for cell in range(cellsPopulationSize)]
                for memUniqueIdx, cellIdx in enumerate(cells.mem_to_cells):
                    cells_mems[cellIdx].append(sim.dd_time[timestampIdx][:, memUniqueIdx])

                cells_permeabilities = []
                for cellMembranes in cells_mems:
                    cells_permeabilities.append(np.mean(cellMembranes, axis=0))
                cells_permeabilities = np.asarray(cells_permeabilities) # N, 4

                # concat Vmem values with perms values
                inputVmem = np.concatenate((inputVmem.reshape((-1, 1)), cells_permeabilities), axis=1) # N, 5

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
                
                #print("inputVmem length: {}".format(inputVmem.shape[0]))
                #print("Configs length: {}".format(configs.shape[0]))
                #print("outputVmem length: {}".format(outputVmem.shape[0]))
                filePath = '/tmp/example.npy'
                np.save(filePath, np.asarray([
                    inputVmem,
                    simConfigsEncoded,
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