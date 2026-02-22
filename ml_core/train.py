import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

# Adjust imports based on your execution path
from models import OmniGuardNet
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_pipeline.dataset_builder import OmniGuardDataset

def train_model():
    # --- Configuration ---
    BATCH_SIZE = 32
    EPOCHS = 15
    LEARNING_RATE = 0.001
    TABULAR_DIM = 2 # Number of features from C++ engine
    
    # Detect hardware acceleration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training on device: {device}")

    # --- Data Loading ---
    dataset = OmniGuardDataset(
        data_dir="../dataset",
        metadata_file="train_metadata.json"
    )
    
    # pin_memory=True ensures fast data transfer from CPU RAM to GPU VRAM
    dataloader = DataLoader(
        dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True, 
        num_workers=4, 
        pin_memory=True 
    )

    # --- Model Setup ---
    model = OmniGuardNet(tabular_feature_dim=TABULAR_DIM).to(device)
    criterion = nn.BCELoss() # Binary Cross Entropy for 0/1 classification
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    # --- Training Loop ---
    model.train()
    best_loss = float('inf')
    
    for epoch in range(EPOCHS):
        epoch_loss = 0.0
        correct_preds = 0
        total_preds = 0
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{EPOCHS}")
        
        for images, tabular_features, labels in progress_bar:
            # Move tensors to the GPU asynchronously
            images = images.to(device, non_blocking=True)
            tabular_features = tabular_features.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(images, tabular_features)
            
            # Loss computation & Backpropagation
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            # Statistics
            epoch_loss += loss.item()
            preds = (outputs > 0.5).float()
            correct_preds += (preds == labels).sum().item()
            total_preds += labels.size(0)
            
            progress_bar.set_postfix({'loss': loss.item(), 'acc': correct_preds/total_preds})
            
        avg_loss = epoch_loss / len(dataloader)
        print(f"[*] Epoch {epoch+1} completed. Average Loss: {avg_loss:.4f}")
        
        # Save the best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            os.makedirs("saved_models", exist_ok=True)
            torch.save(model.state_dict(), "saved_models/omniguard_best.pth")
            print("[+] New best model saved!")

if __name__ == "__main__":
    train_model()