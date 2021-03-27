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
    resetFolders = input("Clean Folder? (y/n)")
    if (resetFolders == "y"):
        if (not os.path.exists('analysis/data')):
            os.makedirs('analysis/data')

        if (not os.path.exists('analysis/data/visualize')):
            os.makedirs('analysis/data/visualize')

        if (not os.path.exists('analysis/data/validate')):
            os.makedirs('analysis/data/validate')

        shutil.rmtree('storage/validation')
        os.makedirs('storage/validation')

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
            if ('cells' not in f):
                examplesIDs.append(f.split(".")[0])
        print(len(examplesIDs))

    #visualizeVmems(examplesIDs)
    validate(examplesIDs)

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
    model_PATH = "storage/model.pth"
    model = modelClass.Net(298, 250)
    #model = torch.load(model_PATH)
    model.load_state_dict(torch.load(model_PATH))

    # Load Helper data
    with open("storage/validation/cells.pkl".format(), "rb") as f:
        cells = pickle.load(f)

    CellsObj = namedtuple('CellsObj', 'cell_verts xmin xmax ymin ymax')
    cells = CellsObj(cell_verts=cells['cell_verts'], xmin=cells['xmin'], xmax=cells['xmax'], ymin=cells['ymin'], ymax=cells['ymax'])
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
        x, y = np.load('storage/validation/{}.npy'.format(exampleID), allow_pickle = True)
        x = x.reshape(1, -1).astype(np.float32)
        Vmems = y[:cellsNum]
        VmemsPred = model(torch.from_numpy(x)).cpu().detach().numpy().reshape(-1)[:cellsNum]
        results['simulation'].extend([exampleID.split("_")[0] for _ in range(Vmems.shape[0])])
        results['ID'].extend([exampleID for _ in range(Vmems.shape[0])])
        results['trueVmem'].extend(Vmems)
        results['predictedVmem'].extend(VmemsPred)
        results['distance'].extend(np.absolute(Vmems - VmemsPred))

    cellsVmemsDistances = pd.DataFrame(results)

    print(cellsVmemsDistances.head())
    simulations = cellsVmemsDistances.simulation.unique()
    print("Simulations: {} | datapoints: {}".format(len(simulations), len(cellsVmemsDistances)))

    #10 random examples per cell difference
    print(">> Cell-wise Vmem Distances (10 simulations) ")
    simulationsSampled = simulations[:10]
    sns_plot = sns.relplot(x="ID", y="distance", data=cellsVmemsDistances[cellsVmemsDistances['simulation'].isin(simulationsSampled)])
    sns_plot.savefig("analysis/data/validate/vmem_distances.png")

    print(">> Correlation Vmem True vs Predicted by value ")
    sns_plot = sns.relplot(x="trueVmem", y="predictedVmem", data=cellsVmemsDistances.sample(10000, random_state=1))
    sns_plot.axes[0,0].set_xlim(-300,100)
    sns_plot.axes[0,0].set_ylim(-300,100)
    sns_plot.savefig("analysis/data/validate/vmems_predicted_vs_true.png")

    print(">> Correlation Vmem True vs Predicted by value (-100, 100 mV)")
    sns_plot = sns.relplot(x="trueVmem", y="predictedVmem", data=cellsVmemsDistances[(cellsVmemsDistances['trueVmem'] >= -100) & (cellsVmemsDistances['trueVmem'] <= 100) ].sample(10000, random_state=1))
    sns_plot.axes[0,0].set_xlim(-150,150)
    sns_plot.axes[0,0].set_ylim(-150,150)
    sns_plot.savefig("analysis/data/validate/vmems_predicted_vs_true_ranged_100mV.png")

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
    sns_plot = sns.catplot(x="ID", y="percentage", data=displayedThres, kind="bar")
    sns_plot.set_xticklabels([str(thres) for thres in displayedThres['threshold']])
    # add annotations one by one with a loop
    for idx, (_, row) in enumerate(displayedThres.iterrows()):
        plt.text(idx - 0.25, row['percentage'] + 0.01, '{:.2f} %'.format(row['percentage'] * 100), horizontalalignment='left', size='medium', color='black', weight='semibold')
    cellsVmemsMatching.to_csv("analysis/data/validate/simulations_matching_thresholds.csv")
    sns_plot.savefig("analysis/data/validate/simulations_matching_thresholds.png")

    print(">> Prediction Accuracy Different Vmems Threshold 5")
    data = pd.DataFrame(cellsVmemsDistances['trueVmem']).astype(int)
    data['matching'] = cellsVmemsDistances['distance'] <= 5
    sns_plot = sns.relplot(x="trueVmem", y="matching", data=data, kind="line", ci="sd")
    sns_plot.savefig("analysis/data/validate/truevmem_vs_accuracy_thres_5.png")

    print(">> Prediction Accuracy Different Vmems Threshold 1")
    data = pd.DataFrame(cellsVmemsDistances['trueVmem'])
    data['matching'] = cellsVmemsDistances['distance'] <= 1
    sns_plot = sns.relplot(x="trueVmem", y="matching", data=data, kind="line", ci="sd")
    sns_plot.savefig("analysis/data/validate/truevmem_vs_accuracy_thres_1.png")

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