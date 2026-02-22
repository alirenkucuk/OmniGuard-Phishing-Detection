import torch
import torch.nn as nn

class URLTextProcessor(nn.Module):
    """
    An LSTM-based network to process the raw character sequence of a URL.
    Captures sequential anomalies that statistical features might miss.
    """
    def __init__(self, vocab_size: int = 100, embedding_dim: int = 32, hidden_dim: int = 64):
        super(URLTextProcessor, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embedding_dim)
        
        # LSTM to process character embeddings
        self.lstm = nn.LSTM(
            input_size=embedding_dim, 
            hidden_size=hidden_dim, 
            num_layers=2, 
            batch_first=True, 
            dropout=0.2
        )
        
        self.fc = nn.Linear(hidden_dim, 32)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: Tensor of shape (batch_size, sequence_length) containing character indices.
        """
        embedded = self.embedding(x)
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Use the output of the last time step from the top layer
        final_hidden_state = hidden[-1, :, :] 
        
        out = torch.relu(self.fc(final_hidden_state))
        return out