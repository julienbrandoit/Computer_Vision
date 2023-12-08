import tifffile as tiff
import json

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Your group and student ID
GROUP_ID = 2
STUDENT_ID = 3

# The path to the tif file
TIFF_PATH = f"../video/{GROUP_ID}-{STUDENT_ID}.tif"

# Annotation file
ANNOTATION_FILE = f"../all_json/{GROUP_ID}_{STUDENT_ID}.json"

# Delay between frames (in seconds)
DELAY = 10

if __name__ == "__main__":

    # Loading the data
    annotations = json.load(open(ANNOTATION_FILE))
    frames = tiff.imread(TIFF_PATH)[:50]

    assert len(frames) == len(annotations), "Number of frames and annotations do not match, you should have 50 frames"

    # Create colors for each group
    colors = [ color for color in matplotlib.colors.TABLEAU_COLORS ]

    fig = plt.figure(figsize=(8, 5))

    for annotation_key, frame in zip(annotations, frames):

        annotation = annotations[annotation_key]

        boxes = annotation["boxes"]
        cells = annotation["cells"]

        for box in boxes:
            # Draw a bounding box on the frame, with a different color for each group
            x, y, width, height, group = box
            bounding_box = patches.Rectangle(
                (x, y), width, height, linewidth=1,
                edgecolor=colors[group % len(matplotlib.colors.TABLEAU_COLORS)], facecolor="none"
            )
            plt.gca().add_patch(bounding_box)

        for cell in cells:
            # Show a small colored dot on the frame
            x_center, y_center, cell_id = cell
            plt.scatter(x_center, y_center, color="red", s=1.0)

        # Show, sleep for DELAY sec, clean the figure, and repeat
        plt.title(f"Frame {annotation_key}")
        plt.imshow(frame)
        plt.pause(DELAY)
        plt.clf()

