import random
import numpy as np

def brute_force_placement(cls, width, height, hall_bounds, placed, obstacles, grid_step=0.5):
    """
    Try every possible (x, y) using a grid, until a valid spot is found.
    """
    x_start, y_start, x_end, y_end = hall_bounds
    for x in np.arange(x_start, x_end - width + 1, grid_step):
        for y in np.arange(y_start, y_end - height + 1, grid_step):
            box = [x, y, x + width, y + height]
            if is_valid_placement(box, hall_bounds, placed, obstacles):
                return box
    return None  # If hall is fully packed

def place_stalls_with_constraints(pred_classes, pred_coords, stall_sizes, stall_counts, hall_bounds, obstacles, max_attempts=10000):
    """
    Try model predictions → fallback random → fallback brute-force grid.
    """
    placed_stalls = []
    counts = {1: 0, 2: 0, 3: 0, 4: 0}  # Platinum:1 ... Bronze:4
    hall_w = hall_bounds[2] - hall_bounds[0]
    hall_h = hall_bounds[3] - hall_bounds[1]

    sorted_classes = sorted(stall_counts.items(), key=lambda item: stall_sizes[item[0]][0] * stall_sizes[item[0]][1], reverse=True)

    for cls, required in sorted_classes:
        width, height = stall_sizes.get(cls, (0, 0))

        for _ in range(required):
            placed = False

            # --- Try using model-predicted coords
            for idx in range(len(pred_classes)):
                if int(pred_classes[idx]) != cls:
                    continue
                norm_x, norm_y = pred_coords[idx][:2]
                x = hall_bounds[0] + norm_x * hall_w
                y = hall_bounds[1] + norm_y * hall_h
                box = [x, y, x + width, y + height]
                if is_valid_placement(box, hall_bounds, placed_stalls, obstacles):
                    placed_stalls.append(box + [cls])
                    counts[cls] += 1
                    placed = True
                    break

            if placed:
                continue

            # --- Try random sampling
            for _ in range(max_attempts):
                rand_x = random.uniform(hall_bounds[0], hall_bounds[2] - width)
                rand_y = random.uniform(hall_bounds[1], hall_bounds[3] - height)
                box = [rand_x, rand_y, rand_x + width, rand_y + height]
                if is_valid_placement(box, hall_bounds, placed_stalls, obstacles):
                    placed_stalls.append(box + [cls])
                    counts[cls] += 1
                    placed = True
                    break

            if placed:
                continue

            # --- Final fallback: grid-based brute-force
            fallback_box = brute_force_placement(cls, width, height, hall_bounds, placed_stalls, obstacles)
            if fallback_box:
                placed_stalls.append(fallback_box + [cls])
                counts[cls] += 1
            else:
                print(f"⚠️ Stall of class {cls} could not be placed after all fallbacks.")

    return placed_stalls

def iou(box1, box2):
    xA = max(box1[0], box2[0])
    yA = max(box1[1], box2[1])
    xB = min(box1[2], box2[2])
    yB = min(box1[3], box2[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    unionArea = box1Area + box2Area - interArea
    return interArea / unionArea if unionArea != 0 else 0

def is_valid_placement(box, hall_bounds, placed, obstacles):
    x1, y1, x2, y2 = box

    # 1. Inside hall
    if not (hall_bounds[0] <= x1 <= x2 <= hall_bounds[2] and
            hall_bounds[1] <= y1 <= y2 <= hall_bounds[3]):
        return False

    # 2. No overlap with obstacles
    for obs in obstacles:
        if iou(box, obs) > 0:
            return False

    # 3. No overlap with other stalls
    for other in placed:
        if iou(box, other[:4]) > 0:
            return False

    return True

import uuid
import json

TIER_MAP = {1: "platinum", 2: "gold", 3: "silver", 4: "bronze"}

def convert_to_website_format_with_existing(final_stalls, original_json):
    hall_area = original_json["hallArea"]
    hall_width = hall_area["width"]
    hall_height = hall_area["height"]

    # Start with original shapes (obstacles + entry/exit)
    merged_shapes = original_json.get("shapes", [])

    # Add predicted stalls
    for stall in final_stalls:
        x1, y1, x2, y2, cls = map(float, stall[:])  # Ensure float64
        cls = int(stall[4])  # Class must be int

        merged_shapes.append({
            "id": str(uuid.uuid4().int)[:13],
            "type": "rectangle",
            "x": x1*4,
            "y": y1*4,
            "width": (x2 - x1)*4,
            "height": (y2 - y1)*4,
            "points": [],
            "category": "stall",
            "tier": TIER_MAP.get(cls, "unknown")
        })

    # Final structure
    final_layout = {
        "hallArea": {"width": hall_width, "height": hall_height},
        "shapes": merged_shapes
    }

    return final_layout