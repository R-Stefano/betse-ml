import analysis.visualize as vis
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def visualize():
    '''

    '''
    vis.run()

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