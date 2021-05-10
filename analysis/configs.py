import os
import numpy as np
import torch 

bucketName = "betse-ml"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './prepare/generate-worker.json'
destFolder = "storage/validation/"
modelName = ""
resultsFolder = ""

configsMax = np.asarray([1.000e-03, 3.001e+01, 5.000e+00, 1.000e+00, 2.900e+01, 3.000e+01, 1.000e+00, 1.000e+03, 1.000e+00, 2.900e+01, 3.000e+01, 1.000e+00, 1.000e+03, 6.000e+00])
inputMax = np.asarray([9.67282725e+01, 2.38187506e-14, 4.26570805e-14, 1.00000000e-19, 1.00100000e-16, 1.57613151e-04, 1.58591705e-04, 1.45046219e+02, 6.83499903e+00, 1.00000000e+01, 1.40004629e+02, 1.51119623e+02, 1.42125226e+02, 1.35000000e+02, 6.07082663e+01])

def preprocess(x, confs):
    # Normalize Data
    x[:, 0] /= 100
    x[:, 1:] /= inputMax[1:].reshape(1,-1)
    confs /= configsMax

    #Exand inputs dimentions [250, M] -> [1, 250, M] & [L] -> [1, L]
    x = np.expand_dims(x, axis=0).astype(np.float32)
    confs = np.expand_dims(confs, axis=0).astype(np.float32)
    
    # Prepare for pytorch
    x = torch.from_numpy(x)
    confs = torch.from_numpy(confs)
    return x, confs

def postprocess(output):
    # Regression model
    #output = output * 100

    #Classificiation Model
    output = np.argmax(output, axis=-1)
    output -= 100
    return output