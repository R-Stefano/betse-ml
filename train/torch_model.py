import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, input_size, output_size):
        super(Net, self).__init__()
        size = 512
        self.layers = [
            nn.Linear(input_size, size),
            nn.Linear(size, size),
            nn.Linear(size, size),
            nn.Linear(size, size),
            nn.Linear(size, size),
            nn.Linear(size, size),
            nn.Linear(size, size)
        ]

        self.last_fc = nn.Linear(size, output_size)

    # x represents our data
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
            x = F.relu(x)
        output = self.last_fc(x)
        return output