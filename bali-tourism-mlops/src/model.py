import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

class SimpleLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=32):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def train_model(model, X, y, epochs=20, batch_size=32, lr=0.001,
                reset_every=None, reset_ratio=None, verbose=False):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    Xt = torch.tensor(X, dtype=torch.float32).to(device)
    yt = torch.tensor(y, dtype=torch.float32).view(-1,1).to(device)
    dataset = TensorDataset(Xt, yt)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        for bx, by in loader:
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
        if reset_every and (epoch+1) % reset_every == 0:
            with torch.no_grad():
                for p in model.parameters():
                    if p.requires_grad:
                        n = p.numel()
                        n_reset = max(1, int(n * reset_ratio))
                        idx = torch.randperm(n)[:n_reset]
                        p.data.view(-1)[idx] = torch.randn(n_reset, device=p.device) * 0.01
            if verbose:
                print(f"Reset at epoch {epoch+1}")
    return model

def predict(model, X):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    with torch.no_grad():
        Xt = torch.tensor(X, dtype=torch.float32).to(device)
        pred = model(Xt).cpu().numpy()
    return pred.squeeze()