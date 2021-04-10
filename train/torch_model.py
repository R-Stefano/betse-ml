import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
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
        
class RNNNet(nn.Module):
    def __init__(self, input_size, configs_size, hidden_state_size=128, num_layers=1):
        super().__init__()
        self.rnn = nn.LSTM(input_size, hidden_state_size, num_layers, batch_first=True)
        self.config_h = nn.Linear(configs_size, hidden_state_size)
        self.config_c = nn.Linear(configs_size, hidden_state_size)

        self.last_fc = nn.Linear(hidden_state_size, 1)

    # x represents our data
    def forward(self, x, configs):
        h0 = torch.unsqueeze(self.config_h(configs), 0)
        c0 = torch.unsqueeze(self.config_c(configs), 0)

        output, (hn, cn) = self.rnn(x, (h0, c0))
        output = torch.squeeze(self.last_fc(output)) # N, 250, 128 -> N, 250, 1 -> N, 250
        return output