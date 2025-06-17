# Flask Layout API - app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import json
from layoutregressor import LayoutRegressor
from utils import (
    place_stalls_with_constraints,
    convert_to_website_format_with_existing
)

# === Flask Setup ===
app = Flask(__name__)
CORS(app)

# === Model Config ===
INPUT_DIM = 12
MAX_STALLS = 250
NUM_CATEGORIES = 5
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === Load Trained Model ===
model = LayoutRegressor(INPUT_DIM, MAX_STALLS, num_categories=NUM_CATEGORIES).to(DEVICE)
model.load_state_dict(torch.load("layout_model.pt", map_location=DEVICE))
model.eval()

# === Prediction Route ===
@app.route("/predict", methods=["POST"])
def predict():
    try:
        uploaded_file = request.files["file"]
        user_inputs_json = request.form["userInputs"]
        user_inputs = json.loads(user_inputs_json)

        raw = json.load(uploaded_file)

        hall_w = round((raw["hallArea"]["width"])/4, 2)
        hall_h = round((raw["hallArea"]["height"])/4, 2)
        hall_bounds = [0, 0, hall_w, hall_h]

        # Extract obstacles
        obstacles = []
        for shape in raw["shapes"]:
            x1 = round((shape["x"])/4, 2)
            y1 = round((shape["y"])/4, 2)
            x2 = x1 + round((shape["width"])/4, 2)
            y2 = y1 + round((shape["height"])/4, 2)
            obstacles.append([x1, y1, x2, y2])

        # Format user inputs
        counts = {}
        sizes = {}
        labels = {1: "Platinum", 2: "Gold", 3: "Silver", 4: "Bronze"}
        for i in range(1, 5):
            label = labels[i]
            tier_data = user_inputs[label]
            counts[i] = tier_data["count"]
            sizes[i] = (tier_data["width"], tier_data["height"])

        # Create input tensor
        feature_list = []
        for i in range(1, 5):
            feature_list.extend([counts[i], sizes[i][0], sizes[i][1]])
        x_tensor = torch.tensor([feature_list], dtype=torch.float32).to(DEVICE)

        # Predict
        class_logits, box_preds = model(x_tensor)
        pred_classes = torch.argmax(class_logits, dim=-1).cpu().numpy()
        pred_coords = box_preds.detach().cpu().numpy()

        # Post-process
        final_stalls = place_stalls_with_constraints(
            pred_classes[0], pred_coords[0], sizes, counts, hall_bounds, obstacles
        )
        final_layout = convert_to_website_format_with_existing(final_stalls, raw)

        return jsonify({"status": 200, "layout": final_layout})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
