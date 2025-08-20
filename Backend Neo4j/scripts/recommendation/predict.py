# ============================
# Predictor (Federated NN) - Returns ranked policies
# ============================

import torch
import torch.nn as nn
import pickle
import numpy as np
import pandas as pd

# --------------------
# Config
# --------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --------------------
# Model Definition (same as training)
# --------------------
class InsuranceNN(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.4)

    def forward(self, x):
        x = self.relu(self.fc1(x)); x = self.dropout(x)
        x = self.relu(self.fc2(x)); x = self.dropout(x)
        x = self.relu(self.fc3(x)); x = self.dropout(x)
        return self.fc4(x)

# --------------------
# Load Artifacts
# --------------------
with open("artifacts/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

with open("artifacts/india_scaler.pkl", "rb") as f:
    india_scaler = pickle.load(f)

# Get input_dim + num_classes
input_dim = india_scaler.mean_.shape[0]
num_classes = len(label_encoder.classes_)

# Load model
model = InsuranceNN(input_dim, num_classes).to(DEVICE)
model.load_state_dict(torch.load("artifacts/federated_nn_model.pth", map_location=DEVICE))
model.eval()

# --------------------
# Prediction Function
# --------------------
def predict_policies(user_input: dict):
    # Convert to DataFrame for consistency
    df = pd.DataFrame([user_input])

    # Keep only numeric features (must match training order)
    X = df.select_dtypes(include=[np.number]).values

    # Scale
    X = india_scaler.transform(X)

    # Convert to tensor
    tensor = torch.tensor(X, dtype=torch.float32).to(DEVICE)

    # Run through NN
    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    # Map back to class labels (policy names)
    policy_map = {
        "0": "Basic",
        "1": "Standard",
        "2": "Gold",
        "3": "Premium"
    }

    # Check if encoder stored ints (0,1,2,3) → then use our manual map
    if all(str(cls).isdigit() for cls in label_encoder.classes_):
        classes = [policy_map[str(c)] for c in range(len(probs))]
    else:
        classes = label_encoder.inverse_transform(np.arange(len(probs)))

    ranked = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)

    return {
        "user_input": user_input,
        "ranked_policies": [
            {"policy": str(c), "probability": round(float(p), 4)} for c, p in ranked
        ],
        "best_recommendation": str(ranked[0][0])
    }

# --------------------
# Test Run
# --------------------
if __name__ == "__main__":
    test_user = {
        "Age": 32,
        "Claim Amount (INR)": 50000,
        "Claim Status": 1,
        "Insurance Type": 2,
        "Annual Premium (INR)": 1500,
        "Risk Score": 70
    }
    result = predict_policies(test_user)
    print("✅ Prediction Result:")
    print(result)
