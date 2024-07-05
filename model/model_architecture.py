from torch import nn
import torch.nn.functional as F
import torch


class Net(nn.Module):
    def __init__(self, base_model, n_features):
        super(Net, self).__init__()
        self.layer0 = nn.Sequential(*list(base_model.children())[:4])
        self.layer1 = nn.Sequential(*list(base_model.layer1))
        self.layer2 = nn.Sequential(*list(base_model.layer2))
        self.layer3 = nn.Sequential(*list(base_model.layer3))
        self.layer4 = nn.Sequential(*list(base_model.layer4))
        self.dense1 = nn.Sequential(nn.Linear(n_features, 128))
        self.dense2 = nn.Sequential(nn.Linear(128, 64))
        self.classif = nn.Sequential(nn.Linear(64, 1))

    def forward(self, x):
        x = self.features(x)
        x = F.avg_pool2d(x, 7)
        x = x.view(x.size(0), -1)
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.classif(x)
        x = torch.sigmoid(x)
        return x

    def features(self, x):
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        return x