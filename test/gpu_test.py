import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Standardize the features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Convert data to PyTorch tensors
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.long)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_tensor, y_tensor, test_size=0.2, random_state=42)

# Define the neural network model
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(4, 64)  # 4 input features, 64 hidden units
        self.fc2 = nn.Linear(64, 3)  # 64 hidden units, 3 output classes

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Instantiate the model and move it to GPU if available
model = SimpleNN()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Training loop
epochs = 100000
for epoch in range(epochs):
    model.train()  # Set the model in training mode
    optimizer.zero_grad()  # Zero gradients

    # Forward pass
    outputs = model(X_train.to(device))
    loss = criterion(outputs, y_train.to(device))

    # Backward pass and optimization
    loss.backward()
    optimizer.step()

    if epoch % 100 == 0:
        print(f"Epoch {epoch}/{epochs} - Loss: {loss.item():.4f}")

# Evaluation on the test set
model.eval()  # Set the model in evaluation mode
with torch.no_grad():
    outputs = model(X_test.to(device))
    _, predicted = torch.max(outputs, 1)
    accuracy = (predicted == y_test.to(device)).sum().item() / len(y_test)
    print(f"Test Accuracy: {accuracy:.4f}")
