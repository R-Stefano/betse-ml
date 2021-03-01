import torch
import os
import numpy as np

import torch_model
import torch.optim as optim
import torch.nn as nn

class Dataset(torch.utils.data.Dataset):
    # Dataset
    def __init__(self, folder, batch_size = 32):
        # Initialization
        self.source = 'data/processed/' + folder + '/'
        
        self._datasetIDs = []
        for i in os.listdir(self.source):
            ID = i.split("_")[1].split(".")[0]
            self._datasetIDs.append(ID) 
        self.batch_size = batch_size

    def shuffle(self):
        #Shuffle dataset
        np.random.shuffle(self._datasetIDs)

    def __len__(self):
        #Denotes the total number of samples
        return int(len(self._datasetIDs) / self.batch_size)

    def __getitem__(self, index):
        # Load data and return example
        i_start = index * self.batch_size
        i_end = i_start + self.batch_size

        inputData = []
        labelData = []
        batchIDs = self._datasetIDs[i_start : i_end]
        for exampleID in batchIDs:
            x, y = np.load(self.source + 'id_' + exampleID + '.npy', allow_pickle = True)
            inputData.append(torch.from_numpy(x))
            labelData.append(torch.from_numpy(y))

        return torch.stack(inputData).float(), torch.stack(labelData).float() 

max_epochs = 100
batch_size = 8

# Generators
training_set = Dataset(folder = 'train', batch_size = batch_size)
training_generator = torch.utils.data.DataLoader(training_set)

validation_set = Dataset(folder = 'validation', batch_size = batch_size)
validation_generator = torch.utils.data.DataLoader(validation_set)

print("Dataset size: {} | train: {} | val: {}".format(len(training_set._datasetIDs) + len(validation_set._datasetIDs), len(training_set._datasetIDs), len(validation_set._datasetIDs)))

net = torch_model.Net(276, 250)
criterion = nn.MSELoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# Loop over epochs
for epoch in range(max_epochs):
    training_set.shuffle()

    training_loss = 0
    validation_loss = 0
    # Training
    for local_batch, local_labels in training_generator:
        x_batch = local_batch[0]
        y_batch = local_labels[0]

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(x_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()

        # print statistics
        training_loss += loss.item()

    # Validation 
    for local_batch, local_labels in validation_generator:
        x_batch = local_batch[0]
        y_batch = local_labels[0]

        outputs = net(x_batch)
        validation_loss += torch.mean((outputs - y_batch)**2)

    print("[EPOCH {}] train loss: {:.3f} | val loss: {:.3f}".format(epoch, training_loss, validation_loss))

torch.save(net.state_dict(), './torch_model.pth')