import analysis.visualize as vis
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
import shutil, pickle
from collections import namedtuple

import analysis.configs as configs
from google.cloud import storage
storage_client = storage.Client()
bucket = storage_client.bucket(configs.bucketName)

def run():
    highEntropyExamplesOnly = False
    modelVersion = 5
    configs.modelName = "model_v{}.pth".format(modelVersion)
    configs.resultsFolder = "data_v{}".format(modelVersion)

    resetFolders = input("Clean Folder? (y/n)")
    if (resetFolders == "y"):
        shutil.rmtree('storage/validation')
        os.makedirs('storage/validation')

    if (not os.path.exists('analysis/{}'.format(configs.resultsFolder))):
        os.makedirs('analysis/{}'.format(configs.resultsFolder))

    if (not os.path.exists('analysis/{}/visualize'.format(configs.resultsFolder))):
        os.makedirs('analysis/{}/visualize'.format(configs.resultsFolder))

    if (not os.path.exists('analysis/{}/validate'.format(configs.resultsFolder))):
        os.makedirs('analysis/{}/validate'.format(configs.resultsFolder))

    if (resetFolders == "y"):
        examplesIDs = []
        #Download validation from GCStorage
        blobs = bucket.list_blobs(prefix="dataset/validation/") # Get list of files
        for idx, blob in enumerate(blobs):
            print(blob.name)
            filename = "{}_{}".format(blob.name.split("/")[-2], blob.name.split("/")[-1])
            examplesIDs.append(filename.split(".")[0])
            blob.download_to_filename(configs.destFolder + filename)  # Download
    else:
        examplesIDs = []
        for f in os.listdir('storage/validation'):
            examplesIDs.append(f.split(".")[0])

    if (highEntropyExamplesOnly):
        examplesIDs = []
        entropy = []
        for f in os.listdir('storage/validation'):
            if ('cells' not in f):
                x, y = np.load('storage/validation/' + f, allow_pickle = True)
                x = x[:250]
                entropy.append(np.mean(np.abs(x-y)))

        idxs = np.argsort(entropy)[::-1][:20]
        entropiesSelected = np.asarray(entropy)[idxs]
        print("Validation Data Entropy: {} | {}".format(np.min(entropiesSelected), np.max(entropiesSelected)))            

        for filename in np.asarray(os.listdir('storage/validation'))[idxs]:
            examplesIDs.append(filename.split(".")[0])

    #visualizeVmems(examplesIDs[:20])
    validate(examplesIDs)
    compare(['data_v{}'.format(version + 1) for version in range(modelVersion)])

def compare(versions):
    data = pd.DataFrame()
    for versionName in versions:
        dataVersion = pd.read_csv("analysis/{}/validate/simulations_matching_thresholds.csv".format(versionName))
        dataVersion['version'] = versionName
        data = data.append(dataVersion)

    sns_plot = sns.relplot(x="threshold", y="percentage", hue="version", kind="line", data=data)
    sns_plot.set(xlabel='Error Threshold', ylabel='Accuracy', title='Prediction Accuracy for different Error Thresholds')
    sns_plot.savefig("analysis/{}/comparison.png".format(configs.resultsFolder))

def visualizeVmems(exampleIDs):
    '''

    '''

    vis.run(exampleIDs)

def validate(exampleIDs):
    '''

    '''
    import torch

    import train.torch_model as modelClass 
    # Open Vmems (Prediction)
    model_PATH = "storage/" + configs.modelName
    #model = modelClass.Net(280, 250)
    model = modelClass.RNNNet(5, 30)
    #model = torch.load(model_PATH)
    model.load_state_dict(torch.load(model_PATH))

    # Load Helper data
    with open("storage/data.betse", "rb") as f:
        sim, cells, _ = pickle.load(f)

    CellsObj = namedtuple('CellsObj', 'cell_verts xmin xmax ymin ymax')
    cellsNum = cells.cell_verts.shape[0]

    #######################

    results = {
        'simulation': [],
        'ID': [],
        'trueVmem': [],
        'predictedVmem': [],
        'distance': []
    }
    for exampleID in exampleIDs:
        # Open Vmems (ground truth)
        x, confs, y = np.load('storage/validation/{}.npy'.format(exampleID), allow_pickle = True)
        x = np.expand_dims(x, axis=0).astype(np.float32) 
        confs = np.expand_dims(confs, axis=0).astype(np.float32) 
        x = torch.from_numpy(x / 100)
        confs = torch.from_numpy(confs)

        Vmems = y[:cellsNum]
        VmemsPred = model(x, confs).cpu().detach().numpy().reshape(-1)[:cellsNum] * 100
        results['simulation'].extend([exampleID.split("_")[0] for _ in range(Vmems.shape[0])])
        results['ID'].extend([exampleID for _ in range(Vmems.shape[0])])
        results['trueVmem'].extend(Vmems)
        results['predictedVmem'].extend(VmemsPred)
        results['distance'].extend(np.absolute(Vmems - VmemsPred))

    cellsVmemsDistances = pd.DataFrame(results)
    populationSampled = 10000

    simulations = cellsVmemsDistances.simulation.unique()
    print("Simulations: {} | datapoints: {}".format(len(simulations), len(cellsVmemsDistances)))

    #10 random examples per cell difference
    print(">> Cell-wise Vmem Distances (10 simulations) ")
    simulationsSampled = simulations[:10]
    sns_plot = sns.relplot(x="ID", y="distance", data=cellsVmemsDistances[cellsVmemsDistances['simulation'].isin(simulationsSampled)], height=10, aspect=2)
    sns_plot.savefig("analysis/{}/validate/vmem_distances.png".format(configs.resultsFolder))

    print(">> Correlation Vmem True vs Predicted by value ")
    popSampled = cellsVmemsDistances.sample(populationSampled, random_state=1)
    sns_plot = sns.lmplot(x="trueVmem", y="predictedVmem", data=popSampled, height=10, aspect=2,  x_estimator=np.mean)
    minVmem = np.min(np.min(popSampled[["trueVmem", "predictedVmem"]]))
    maxVmem = np.max(np.max(popSampled[["trueVmem", "predictedVmem"]]))
    sns_plot.set(xlabel='True Vmem', ylabel='Predicted Vmem', title='Predicted Vmem Vs True Vmem')
    sns_plot.axes[0,0].set_xlim(minVmem + (minVmem * 0.1), maxVmem + (maxVmem * 0.1))
    sns_plot.axes[0,0].set_ylim(minVmem + (minVmem * 0.1), maxVmem + (maxVmem * 0.1))
    sns_plot.savefig("analysis/{}/validate/vmems_predicted_vs_true.png".format(configs.resultsFolder))

    print(">> Predicts Accuracy Different Thresholds")
    data = {
        'ID': [i for i in range(50)],
        'threshold': [i for i in range(50)],
        'percentage': []
    }

    for thres in data['threshold']:
        matched = []
        matched.append(np.asarray(cellsVmemsDistances['distance']) < thres)
        data['percentage'].append(np.mean(matched))

    cellsVmemsMatching = pd.DataFrame(data)
    displayedThres = cellsVmemsMatching[cellsVmemsMatching['threshold'].isin([1, 2, 5, 10, 25, 50])]
    sns_plot = sns.catplot(x="ID", y="percentage", data=displayedThres, kind="bar", height=10, aspect=2)
    sns_plot.set_xticklabels([str(thres) for thres in displayedThres['threshold']])
    # add annotations one by one with a loop
    for idx, (_, row) in enumerate(displayedThres.iterrows()):
        plt.text(idx - 0.25, row['percentage'] + 0.01, '{:.2f} %'.format(row['percentage'] * 100), horizontalalignment='left', size='medium', color='black', weight='semibold')
    cellsVmemsMatching.to_csv("analysis/{}/validate/simulations_matching_thresholds.csv".format(configs.resultsFolder))
    sns_plot.savefig("analysis/{}/validate/simulations_matching_thresholds.png".format(configs.resultsFolder))

    print(">> Prediction Accuracy Different Vmems Threshold 5")
    data = pd.DataFrame(cellsVmemsDistances['trueVmem']).astype(int)
    data['matching'] = cellsVmemsDistances['distance'] <= 5
    sns_plot = sns.catplot(x="trueVmem", y="matching", data=data, kind="bar", height=10, aspect=2)
    sns_plot.set(xlabel='True Vmem', ylabel='Accuracy', title='Prediction Accuracy for Vmem Values (Vmem Distance Threshold 5mV)')
    sns_plot.savefig("analysis/{}/validate/truevmem_vs_accuracy_thres_5.png".format(configs.resultsFolder))

    print(">> Prediction Accuracy Different Vmems Threshold 1")
    data = pd.DataFrame(cellsVmemsDistances['trueVmem']).astype(int)
    data['matching'] = cellsVmemsDistances['distance'] <= 1
    sns_plot = sns.catplot(x="trueVmem", y="matching", data=data, kind="bar", height=10, aspect=2)
    sns_plot.set(xlabel='True Vmem', ylabel='Accuracy', title='Prediction Accuracy for Vmem Values (Vmem Distance Threshold 1mV)')
    sns_plot.savefig("analysis/{}/validate/truevmem_vs_accuracy_thres_1.png".format(configs.resultsFolder))

def visualizeVmemEvolution():
    exampleIdxs = [0, 4, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    dataRuns = pd.DataFrame()
    for exampleIdx in exampleIdxs:
        exampleFolder = 'storage/raw/{}'.format(exampleIdx)
        #get number of csv files
        csvFiles = list(filter(lambda filename: '.csv' in filename, [filename for filename in os.listdir(exampleFolder)]))
        print(len(list(csvFiles)))
        dataPlot = []
        for timestepIdx in range(len(csvFiles)):
            data = pd.read_csv('{}/Vmem2D_{}.csv'.format(exampleFolder, timestepIdx))
            dataPlot.append(data['Vmem [mV]'].values)

        runDataAvgVmem = np.mean(dataPlot, axis=1)
        data = pd.DataFrame(runDataAvgVmem).reset_index()
        data['run'] = [exampleIdx for _ in range(len(data))]
        data.columns = ['timestep', 'vmem', 'runID']

        dataRuns = dataRuns.append(data)

    sns.lineplot(x="timestep", y="vmem", hue="runID", data=dataRuns)
    plt.show()