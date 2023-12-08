import param
import cv2
import random as rng
import tifffile as tf
import numpy as np

import json

import concurrent.futures

kernel_radius_erosion = int(param.mean_radius*param.scale_kernel)
kernel_radius_dilation = int(param.mean_radius*param.scale_kernel*param.dilate_loss)
kernel_erosion = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*kernel_radius_erosion+1, 2*kernel_radius_erosion+1))
kernel_dilation = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*kernel_radius_dilation+1, 2*kernel_radius_dilation+1))

def get_ellipse_bb(ellipse):
    center, axes, angle = ellipse
    
    angle_rad = np.radians(angle)
    # Generate points on the ellipse using parametric equations
    t_values = np.linspace(0, 2*np.pi, 25)
    x_values = center[0] + axes[0]/2 * np.cos(t_values) * np.cos(angle_rad) - axes[1]/2 * np.sin(t_values) * np.sin(angle_rad)
    y_values = center[1] + axes[0]/2 * np.cos(t_values) * np.sin(angle_rad) + axes[1]/2 * np.sin(t_values) * np.cos(angle_rad)
    
    # Find the bounding box of the points
    x, y, w, h = cv2.boundingRect(np.array([x_values, y_values]).T.astype(np.int32)) 
    return x, y, w, h

def in_image(x, w, image_width, border_size = 0):
    return  x - border_size >= param.edge_margin \
            and (x + w + param.edge_margin - border_size) <= image_width \

# Function to process a single frame
def process_frame(f, image):
    filtered_rect = []

    #We scale down the image to reduce the computation time
    image = cv2.resize(image, (0,0), fx=param.scaling_factor, fy=param.scaling_factor)
    _, image_width = image.shape[:2]
    
    #src_gray is the image that we will use to detect the bubbles
    src_gray = image.copy()

    contours, _ = cv2.findContours(src_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for i, c in enumerate(contours):
        if len(c) < 5:
            continue
        hull = cv2.convexHull(c, returnPoints=True)
        hull_l = cv2.arcLength(hull, True)
        
        # The detected countour is to small to be a bubble
        if hull_l < param.min_perim:
            continue

        # The detected countour is too big to be a bubble, it is probably multiple bubbles that are touching each other
        # We try to split them and to detect them individually
        if(hull_l > param.max_perim):

            # We create a masked version of the image with only the current contour (masked by its hull)
            mask = np.zeros_like(src_gray)
            cv2.drawContours(mask, [hull], -1, (255, 255, 255), thickness=cv2.FILLED)
            result = cv2.bitwise_and(src_gray, 1, mask=mask)
            cv2.drawContours(result, [c], -1, (255, 255, 255), thickness=cv2.FILLED)
            result = cv2.copyMakeBorder(result, 0, 0, param.border_size, param.border_size, cv2.BORDER_CONSTANT, value=255)
            result = cv2.copyMakeBorder(result, 0, 0, param.border_size*5, param.border_size*5, cv2.BORDER_CONSTANT, value=0)
            result = cv2.GaussianBlur(result, (15,15), 0)

            bordered_contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for j in range(len(bordered_contours)):
                cv2.drawContours(result, bordered_contours, j, (255, 255, 255), thickness=cv2.FILLED)

            # We erode the masked image to separate the bubbles
            eroded_image = cv2.erode(result, kernel_erosion)
            # We identify connected components and process them one by one
            _, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded_image, connectivity=4)
            for i in range(1, len(stats)):
                #We reconstruct the initial bubbles (before erosion) on the masked version
                mask_blob = (labels == i).astype(np.uint8) * 255
                dilated_blob = cv2.dilate(mask_blob, kernel_dilation)

                ctn_hull, _ = cv2.findContours(dilated_blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for ctn in ctn_hull:
                    ellipse = cv2.fitEllipse(ctn)
                    x, y, w, h = get_ellipse_bb(ellipse)
                    if 2*param.min_radius <= ellipse[1][0] <= 2*param.max_radius and 2*param.min_radius <= ellipse[1][1] <= 2*param.max_radius and in_image(x, w, image_width, border_size = param.border_size + 5*param.border_size):
                        filtered_rect.append((x - (param.border_size + 5*param.border_size), y, w, h))
        else: # The detected countour is a bubble
            ellipse = cv2.fitEllipse(hull)
            x, y, w, h = get_ellipse_bb(ellipse)
            if 2*param.min_radius <= ellipse[1][0] <= 2*param.max_radius and 2*param.min_radius <= ellipse[1][1] <= 2*param.max_radius and in_image(x, w, image_width):
                filtered_rect.append((x, y, w, h))

    if param.tracking:
        # set default ID as 0
        return [[int(element / param.scaling_factor) for element in inner_list] + [0] for inner_list in filtered_rect]
    return [[int(element / param.scaling_factor) for element in inner_list] for inner_list in filtered_rect]

def process_frames_threaded(foreground_masks):
    boxes = [[]]*len(foreground_masks)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_frame, f, np.array(image)): (f, image) for f, image in enumerate(foreground_masks)}
        for future in concurrent.futures.as_completed(futures):
            f, _ = futures[future]
            
            if param.print_frame:
                print(f"- BB : frame {f}")
            try:
                boxes[f] = future.result()
            except Exception as e:
                print(f"Error processing frame {f}: {e}")
    return boxes

def get_bounding_boxes(foreground_masks):  
    # Measure execution time for threaded approach
    boxes = process_frames_threaded(foreground_masks)
    
    if param.output_BB == True:
        output_tiff_stack = tf.TiffWriter(param.output_BB_tif)

        for f, image in enumerate(foreground_masks):
            image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            for rect in boxes[f]:
                x, y, w, h = rect[0:4]
                
                color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
                cv2.rectangle(image_color, (x, y), (x + w, y + h), color, 2)
            output_tiff_stack.save(image_color)
        output_tiff_stack.close()
    
    if param.perf == True:
        with open(param.bb_json_path, 'w') as json_file:
            json.dump(boxes, json_file)

    return boxes
