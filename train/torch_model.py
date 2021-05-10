import torch
import torch.nn as nn
import torch.nn.functional as F

class MLP(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        size = 512
        self.l1 = nn.Linear(input_size, size)
        self.l2 = nn.Linear(size, size)
        self.l3 = nn.Linear(size, size)
        self.l4 = nn.Linear(size, size)
        self.l5 = nn.Linear(size, size)
        self.l6 = nn.Linear(size, size)
        self.l7 = nn.Linear(size, size)

        self.last_fc = nn.Linear(size, output_size)

    # x represents our data
    def forward(self, x, confs):
        x = torch.cat([x, confs], dim=1)
        x = F.relu(self.l1(x))
        x = F.relu(self.l2(x))
        x = F.relu(self.l3(x))
        x = F.relu(self.l4(x))
        x = F.relu(self.l5(x))
        x = F.relu(self.l6(x))
        x = F.relu(self.l7(x))
            
        output = self.last_fc(x)
        return output
        
class RNNNet(nn.Module):
    def __init__(self, input_size, configs_size, output_size = 1, hidden_state_size=128, num_layers=1, bidirectional=False):
        
        super().__init__()
        self.rnn = nn.LSTM(input_size, hidden_state_size, num_layers, bidirectional=bidirectional, batch_first=True)
        self.config_h = nn.Linear(configs_size, hidden_state_size)
        self.config_c = nn.Linear(configs_size, hidden_state_size)

        lstmOutput = hidden_state_size
        if (bidirectional):
          lstmOutput *= 2
        self.last_fc = nn.Linear(lstmOutput, output_size)

    # x represents our data
    def forward(self, x, configs):
        multiplier = 1 * self.rnn.num_layers
        if (self.rnn.bidirectional):
          multiplier *= 2

        h0 = torch.unsqueeze(self.config_h(configs), 0).repeat(multiplier, 1, 1)
        c0 = torch.unsqueeze(self.config_c(configs), 0).repeat(multiplier, 1, 1)

        output, (hn, cn) = self.rnn(x, (h0, c0))
        output = self.last_fc(output) # N, 250, 128 -> N, 250, out_size
        return output