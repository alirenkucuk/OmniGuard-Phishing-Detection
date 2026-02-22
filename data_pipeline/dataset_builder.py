import os
import json
import torch
from torch.utils.data import Dataset
from PIL import Image
from torchvision import transforms

class OmniGuardDataset(Dataset):
    """
    Custom PyTorch Dataset for loading multi-modal phishing data.
    Loads screenshots (visual) and tabular features simultaneously.
    """
    def __init__(self, data_dir: str, metadata_file: str, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        
        # Load metadata containing labels and pre-extracted features
        metadata_path = os.path.join(data_dir, metadata_file)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        # Default image transformations if none provided
        if self.transform is None:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                     std=[0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        item = self.metadata[idx]
        
        # 1. Load Visual Data (Screenshot)
        img_path = os.path.join(self.data_dir, "screenshots", item['screenshot_file'])
        try:
            image = Image.open(img_path).convert('RGB')
            image = self.transform(image)
        except Exception as e:
            # Fallback to a blank tensor if image is corrupted
            image = torch.zeros((3, 224, 224))
            
        # 2. Load Tabular Data (From C++ engine & Text processor)
        # Assuming features like [url_length, entropy, tld_risk_score, ...]
        tabular_features = torch.tensor(item['features'], dtype=torch.float32)
        
        # 3. Load Label (1 for Phishing, 0 for Legitimate)
        label = torch.tensor([item['label']], dtype=torch.float32)
        
        return image, tabular_features, label