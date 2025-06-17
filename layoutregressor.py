import torch
import torch.nn as nn

class LayoutRegressor(nn.Module):                                                   #DEFINING MODEL
    def __init__(self, input_dim, max_stalls, num_categories=5, hidden_dim=256):    # THE INPUTS
        super().__init__()
        self.max_stalls = max_stalls
        self.num_categories = num_categories

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # Separate heads for classification and bounding box (x, y, w, h)
        self.class_head = nn.Linear(hidden_dim, max_stalls * num_categories)
        self.box_head   = nn.Linear(hidden_dim, max_stalls * 4)  # x, y, w, h

    def forward(self, x):
        """
        Input:
            x: [B, input_dim] → user inputs
        Output:
            - class_logits: [B, max_stalls, num_categories]
            - box_outputs:  [B, max_stalls, 4] (x, y, w, h)
        """
        encoded = self.encoder(x)  # [B, hidden_dim]

        class_logits = self.class_head(encoded)               # [B, max_stalls * num_categories]
        class_logits = class_logits.view(-1, self.max_stalls, self.num_categories)

        box_outputs = self.box_head(encoded)                  # [B, max_stalls * 4]
        box_outputs = box_outputs.view(-1, self.max_stalls, 4)

        return class_logits, box_outputs   