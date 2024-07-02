import numpy as np
import pytorch_lightning as pl
from pytorch_lightning import Trainer
from torch.utils.data import Dataset, DataLoader
import torch
from unittest import TestCase
from unittest.mock import patch
from torch.nn import functional as F

# Define the 'RandomDataset' object
class RandomDataset(Dataset):
    def __init__(self, size, len):
        self.len = len
        self.data = torch.randn(len, size)

    # Method to get item from dataset
    def __getitem__(self, index):
        return self.data[index]

    # method to get length of dataset
    def __len__(self):
        return self.len

# Create an instance of the `RandomDataset`
size = 2
len  = 1000
dataset = RandomDataset(size, len)

# Split the dataset into training and testing datasets
train, test = torch.utils.data.random_split(dataset, [800, 200])

# Load the training and testing data
train_loader = DataLoader(dataset=train, batch_size=100)
test_loader = DataLoader(dataset=test, batch_size=100)

# Define the model class
class Model(pl.LightningModule):
    def __init__(self):
        super(Model, self).__init__()
        self.layer = torch.nn.Linear(2, 2)

    # Forward propagation
    def forward(self, x):
        return self.layer(x)

    # Computing the loss
    def compute_loss(self, batch):
        loss = F.mse_loss(self(batch), batch)
        return loss

    # Defing the training step
    def training_step(self, batch, batch_nb):
        loss = self.compute_loss(batch)
        result = pl.TrainResult(loss)
        result.log('train_loss', loss)
        return result

    # Defining the validation steps
    def validation_step(self, batch, batch_nb):
        loss = self.compute_loss(batch)
        result = pl.EvalResult(checkpoint_on=loss)
        result.log('val_loss', loss)
        return result

    # Defining the configure_optimizers method
    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.02)

    # Returning the training data loader
    def train_dataloader(self):
        return train_loader

    # Returning the testing data loader
    def test_dataloader(self):
        return test_loader

# Creating instance of the 'Model' class
model = Model()

# Define a trainer object
trainer = Trainer(max_epochs=100)

# Fit the model
trainer.fit(model)

# Mock class for testing
class TestModel(TestCase):

  @patch('__main__.Model', autospec=True)
  def test_model(self, mock_model):
      instance = mock_model.return_value
      trainer = Trainer(max_epochs=100)
      trainer.fit(instance)
      self.assertTrue(mock_model.called)
      mock_model.assert_called_once_with()

# Running the test
if __name__ == "__main__":
    test_model = TestModel()
    test_model.test_model()