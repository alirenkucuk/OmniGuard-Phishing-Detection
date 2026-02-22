import torch
import torch.nn as nn
import torchvision.models as models

class OmniGuardNet(nn.Module):
    """
    Multi-Modal Neural Network for Phishing Detection.
    Fuses visual features (screenshots) with statistical/NLP features (URL/DOM).
    """
    def __init__(self, tabular_feature_dim: int, hidden_dim: int = 128):
        super(OmniGuardNet, self).__init__()
        
        # Branch 1: Visual Feature Extractor (Pre-trained ResNet18)
        # We freeze the early layers and only train the final layers for our domain
        resnet = models.resnet18(pretrained=True)
        self.visual_extractor = nn.Sequential(*list(resnet.children())[:-1]) # Remove final FC layer
        self.visual_fc = nn.Linear(resnet.fc.in_features, hidden_dim)

        # Branch 2: Tabular/Statistical Feature Extractor (From C++ Engine)
        self.tabular_extractor = nn.Sequential(
            nn.Linear(tabular_feature_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, hidden_dim)
        )

        # Fusion Layer: Combining Visual and Tabular branches
        self.fusion_classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
            nn.Sigmoid() # Binary classification: 1 (Phishing), 0 (Legitimate)
        )

    def forward(self, image: torch.Tensor, tabular_data: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for the multi-modal network.
        """
        # Process visual data
        v_features = self.visual_extractor(image)
        v_features = v_features.view(v_features.size(0), -1) # Flatten
        v_features = torch.relu(self.visual_fc(v_features))

        # Process tabular data
        t_features = self.tabular_extractor(tabular_data)

        # Concatenate both feature spaces
        combined_features = torch.cat((v_features, t_features), dim=1)

        # Final classification
        output = self.fusion_classifier(combined_features)
        return output