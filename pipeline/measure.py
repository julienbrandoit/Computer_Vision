import param
import json
import numpy as np
import re
import matplotlib.pyplot as plt
import pandas as pd
import math

def compute_perf(s, n):

    score = compute_bb_perf(s, n)

    tracking_acc = 0
    if param.tracking:
        tracking_acc = compute_tracking_perf(s, n)

    cells, distance, norm = compute_dc_perf(s, n)

    return score, cells, distance, norm, tracking_acc

def compute_bb_perf(s, n):
    def calculate_iou(box1, box2):
        if param.tracking:
            x1, y1, w1, h1, _ = box1
        else:
            x1, y1, w1, h1 = box1
        x2, y2, w2, h2, _= box2

        # Calculate coordinates of intersection rectangle
        x_intersection = max(x1, x2)
        y_intersection = max(y1, y2)
        w_intersection = min(x1 + w1, x2 + w2) - x_intersection
        h_intersection = min(y1 + h1, y2 + h2) - y_intersection

        # Check if there is no intersection (negative values for width or height)
        if w_intersection <= 0 or h_intersection <= 0:
            return 0.0  # No intersection, Jaccard Index is 0

        # Calculate area of intersection rectangle
        area_intersection = w_intersection * h_intersection

        # Calculate area of union rectangle
        area_union = w1 * h1 + w2 * h2 - area_intersection

        # Calculate Jaccard Index
        iou = area_intersection / area_union

        return iou

    predicted_boxes = []
    true_boxes = []
    with open(param.bb_json_path, 'r') as json_file:
        predicted_boxes = json.load(json_file)
    with open(param.all_json_path.format(s, n), 'r') as json_file:
        my_dict = json.load(json_file)
        for key in my_dict:
            # Check if the key matches the desired pattern
            if re.match(r'\w+_\w+_frame_\d+', key):
                true_boxes.append(my_dict[key]['boxes'])
    score = []

    true_pos = 0
    j_m = 0
    false_pos = 0
    false_neg = 0
    jaccard = 0
    for frame, boxes in enumerate(predicted_boxes):
        if frame >= len(true_boxes):
            break
        if len(boxes) == len(true_boxes[frame]):
            true_pos += len(boxes)
            j_m += len(boxes)

            for b_p in boxes:
                best_dist = np.inf
                best_box = None
                for b_g in true_boxes[frame]:
                    dist = np.sqrt((b_p[0] - b_g[0])**2 + (b_p[1] - b_g[1])**2)
                    if dist < best_dist:
                        best_dist = dist
                        best_box = b_g
                j = calculate_iou(b_p, best_box)
                jaccard += j

        elif len(boxes) < len(true_boxes[frame]):
            dif = len(true_boxes[frame]) - len(boxes)
            true_pos += len(boxes)
            j_m += len(boxes)
            false_neg += dif
            for b_p in boxes:
                best_dist = np.inf
                best_box = None
                for b_g in true_boxes[frame]:
                    dist = np.sqrt((b_p[0] - b_g[0])**2 + (b_p[1] - b_g[1])**2)
                    if dist < best_dist:
                        best_dist = dist
                        best_box = b_g
                j = calculate_iou(b_p, best_box)
                jaccard += j
        elif len(boxes) > len(true_boxes[frame]):
            dif = len(boxes) - len(true_boxes[frame])
            true_pos += len(true_boxes[frame])
            false_pos += dif

    score = [true_pos/(true_pos+false_pos+false_neg), false_pos/(true_pos+false_pos+false_neg), false_neg/(true_pos+false_pos+false_neg), jaccard/j_m]
    return score


def compute_tracking_perf(s, n):
    true_boxes = []
    with open(param.tr_json_path, 'r') as json_file:
        predicted_boxes = json.load(json_file)

    with open(param.all_json_path.format(s, n), 'r') as json_file:
        my_dict = json.load(json_file)
        for key in my_dict:
            # Check if the key matches the desired pattern
            if re.match(r'\w+_\w+_frame_\d+', key):
                true_boxes.append(my_dict[key]['boxes'])

    id_dict = {}
    wrong_count = 0
    total_count = 0
    for frame, boxes in enumerate(predicted_boxes[0:50]):
        for box in boxes:
            total_count += 1
            id_t = box[4]
            x = box[0]
            true_id = None  # if not identified in annotation
            true_x = np.inf
            for box in true_boxes[frame]:
                if abs(x - box[0]) < abs(x - true_x):
                    true_id = box[4]
                    true_x = box[0]
            if id_t not in id_dict:
                id_dict[id_t] = true_id
            else:
                if true_id != id_dict[id_t]:
                    wrong_count += 1

    accuracy = (total_count - wrong_count) / total_count * 100
    return accuracy


def compute_distance(real, comp):
    def euclidian_dist(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    dist1 = 0
    dist2 = 0

    for c in comp:
        dist1 += euclidian_dist(c, min(real, key=lambda r: euclidian_dist(c, r)))

    for r in real:
        dist2 += euclidian_dist(r, min(real, key=lambda c: euclidian_dist(c, r)))

    dist1 /= 2*len(comp)
    dist2 /= 2*len(real)
    return dist1+dist2


def get_pos_real_cells(s, n, frame):
    annotations_json = json.load(open(param.all_json_path.format(s, n)))
    annotations = annotations_json[f"{s}_{n}_frame_{frame}"]
    boxes = annotations['boxes']

    df = pd.DataFrame(annotations['cells'], columns=['x', 'y', 'id'])
    cells_df = df.groupby('id')[['x', 'y']].apply(
        lambda x: x.values.tolist())
    real_cells = [cells_df[boxes[i][-1]] for i in range(len(boxes))]

    return boxes, real_cells


def map_comp_to_real(real_boxes, comp_boxes):
    mapping = []

    for boxe in comp_boxes:
        match = min(real_boxes, key=lambda b: np.sqrt(
            (boxe[0] - b[0])**2 + (boxe[1] - b[1])**2))

        if np.sqrt((boxe[0] - match[0])**2 + (boxe[1] - match[1])**2) > 0.5*param.mean_r:
            mapping.append(-1)
        else:
            mapping.append(real_boxes.index(match))

    return mapping


def get_cells_per_boxes(cells, boxes):
    nb = 0
    for i in cells:
        nb += len(i)

    if len(boxes) == 0:
        return 0
    return nb/len(boxes)


def get_random_cells(X, Y, W, H, length):
    output = []

    R = min(W, H) / 2
    for i in range(length):
        r, theta = [math.sqrt(np.random.randint(0,R))*math.sqrt(R), 2*math.pi*np.random.random()]
        output.append([X + W/2 + r * math.cos(theta), Y + H/2 + r * math.sin(theta)])

    return output


def compute_dc_perf(s, n):
    perf_dc = json.load(open(param.dc_json_path))
    full_cells = perf_dc['cells']
    boxes = perf_dc['boxes']

    nb_boxes = 0
    nb_real_cells = []
    nb_comp_cells = []
    diff_cells = []

    distance_comp = []
    distance_rand = []
    distance_norm = []

    for f in range(30):
        try:
            real_boxes, real_cells = get_pos_real_cells(s, n, f+1)
        except:
            continue

        comp_boxes, comp_cells = boxes[f], full_cells[f]
        mapping = map_comp_to_real(real_boxes, comp_boxes)


        for i, cells in enumerate(comp_cells):

            if mapping[i] == -1:
                continue

            random_cells = get_random_cells(*comp_boxes[i][0:4], len(cells))

            d1 = compute_distance(real_cells[mapping[i]], cells)
            d2 = compute_distance(real_cells[mapping[i]], random_cells)

            distance_comp.append(d1)
            distance_rand.append(d2)
            distance_norm.append(d2/d1)
            
            nb_real = len(real_cells[mapping[i]])
            nb_comp = len(comp_cells[i])

            nb_real_cells.append(nb_real)
            nb_comp_cells.append(nb_comp)

            diff_cells.append((nb_comp - nb_real) / nb_real)

    return (nb_comp_cells, nb_real_cells), (distance_comp, distance_rand), (diff_cells, distance_norm)