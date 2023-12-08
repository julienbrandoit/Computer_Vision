import cv2
import numpy as np
import tifffile as tf
import json
from scipy.stats import multivariate_normal
import param
import random

# Random colors for print
def number_to_random_color(number):
    # Seed the random number generator for reproducibility
    random.seed(number + 10)
    
    # Generate random RGB values
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)

    return (red, green, blue)

# Set the mean and covariance matrix for the 2D Gaussian
mean_s = np.array([param.mean_x, param.mean_y])
covariance_s = np.array([[param.sigma_x**2, 0], [0, param.sigma_y**2]])

# Threshold set by testing on the annotations
threshold = 1e-20

def give_id(last_given_id, boxes, width, next_predicted_boxes, next_keep_position):
    for box in boxes:
        x, y, w, h, last_given_id = box

        # Don't search for the corresponding box in next frame
        # when out of the frame or "less than possible value"
        if width - x - mean_s[0] < param.mean_radius - 2 * 2 * param.sigma_radius:
            continue

        mean_b = [mean_s[0] + x, mean_s[1] + y]
        covariance_b = covariance_s

        pdf = multivariate_normal(mean_b, covariance_b)

        identified_next_frame = False
        for next_box in next_predicted_boxes:
            pdf_value = pdf.pdf((next_box[0], next_box[1]))
            # Reject pdf <= threshold: impossible that it is the matching box
            if pdf_value > threshold:
                identified_next_frame = True
                next_box[4] = box[4] # no 2 match to same bb so can directly change the id

        # Keep in memory when a bounding box should have been identified
        if not identified_next_frame:
            next_keep_position.append([mean_s[0] + x, mean_s[1] + y, w, h, last_given_id])
    return last_given_id

def update_boxes(boxes, first_future_id, delta_position):
    for box in boxes:
        if box[4] >= first_future_id:
            box[4] = box[4] + delta_position

def setIDs(foreground_masks, bounding_boxes):
    for boxes in bounding_boxes:
        boxes.sort(key = lambda x: x[0], reverse=True)
    image_width = len(foreground_masks[0][0])
    # Give id to first non-empty frame
    first_non_empty_frame = 0
    while True:
        if param.print_frame:
            print(f"- Tracking : frame {first_non_empty_frame}")
        # Current frame empty: no id to give
        if bounding_boxes[first_non_empty_frame] == []:    
            first_non_empty_frame += 1
            continue
        # Current frame non-empty: give id starting from 1
        for id, rect in enumerate(bounding_boxes[first_non_empty_frame]):
            rect[4] = id + 1
        break

    keep_position = []
    for i in range(len(bounding_boxes)):
        keep_position.append([])
    last_given_id = 0
    last_given_id_bb = 0
    last_given_id_keep = 0
    # Give an id to the other frames
    for frame, boxes in enumerate(bounding_boxes[first_non_empty_frame:-1]):
        if param.print_frame:
            print(f"- Tracking : frame {frame+1}")
        last_given_id_bb = give_id(last_given_id_bb, boxes, image_width, bounding_boxes[frame+1], keep_position[frame+1])
        last_given_id_keep = give_id(last_given_id_keep, keep_position[frame], image_width, bounding_boxes[frame+1], keep_position[frame+1])
        last_given_id = max(last_given_id_bb, last_given_id_keep)

        # Go through all next bounding boxes and give an id to those who haven't got one
        for position, next_box in enumerate(bounding_boxes[frame+1]):
            if next_box[4] == 0:
                # Check if past position got an ID
                if position-1 >= 0:
                    next_box[4] = bounding_boxes[frame+1][position-1][4] + 1
                else:
                    # Check if a future position got an ID:
                    # in this case, in previous frames, the cell was not identified
                    first_future_id = 0
                    has_future_id_keep = False
                    has_future_id_predicted = False
                    ids_found_predicted = [subarray[4] for subarray in bounding_boxes[frame+1][position+1:]]
                    ids_found_keep = keep_position[frame+1]
                    id_position_futur = 0
                    for id_position, id_value in enumerate(ids_found_predicted):
                        if id_value != 0:
                            first_future_id = id_value
                            id_position_futur = id_position
                            has_future_id_predicted = True
                            break
                    for id_position, box in enumerate(ids_found_keep):
                        # Search only through future cells, i.e. cells that have small x coordinate
                        if box[0] < next_box[0]:
                            if first_future_id > box[4]:
                                first_future_id == box[4]
                                id_position_futur = id_position
                            has_future_id_keep = True
                            break
                    if has_future_id_predicted or has_future_id_keep:
                        # Need to update the other ids to allow the intercalation of the new boxes ID
                        delta_position = id_position_futur + 1
                        for i in range(frame, -1, -1):
                            update_boxes(bounding_boxes[i], first_future_id, delta_position)
                        update_boxes(keep_position[frame+1], first_future_id, delta_position)
                        update_boxes(bounding_boxes[frame+1][position+1:], first_future_id, delta_position)
                        # Intercalate the new boxes ID
                        for i in range(position, delta_position):
                            bounding_boxes[frame+1][position+i][4] = first_future_id + i
                    # If no past or future cell position got an ID:
                    # Give an id that continues the count
                    else:
                        last_given_id = last_given_id + 1
                        next_box[4] = last_given_id

    if param.output_tracking == True:
        output_path = param.output_tracking_tif
        output_tiff_stack = tf.TiffWriter(output_path)

        for f, image in enumerate(foreground_masks):
            image = np.array(image)
            if param.print_frame:
                print(f"- Tracking output: frame {f}")

            image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            for rect in bounding_boxes[f]:
                x, y, w, h, id = rect

                color = number_to_random_color(id)
                cv2.rectangle(image_color, (x, y), (x + w, y + h), color, 2)
            output_tiff_stack.save(image_color)
        output_tiff_stack.close()

    if param.perf == True:
        with open(param.tr_json_path, 'w') as json_file:
            json.dump(bounding_boxes, json_file)
