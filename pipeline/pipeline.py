import tifffile as tf

import param
import BGS
import bounding_boxes_extraction
import tracking
import detect_cells
import measure
import output

import time

class timer:
    def __init__(self):
        self.timer = time.time()

    def get_time(self):
        tmp = self.timer
        self.timer = time.time()
        return self.timer - tmp


"""
start follow this process
    0. EXTRACT ALL FRAMES
    1. BGS
    2. BOUNDING BOXES EXTRACTION
    3. For each bounding box
        3a. TRACKING (optional)
        3b. CELL COUNTING
    4. OUTPUT
    5. MEASURE (optional)
"""
def start(s, n):
    t = timer()

    #0. EXTRACT ALL FRAMES
    input_path = param.input_path.format(s, n)
    tiff_stack = tf.TiffFile(input_path)
    
    video = []
    for page in tiff_stack.pages:
        video.append(page.asarray())

    #1. BGS
    frames, foreground = BGS.BGS(video)
    print(f"== BGS END {t.get_time()}sec ==")

    #2. BOUNDING BOXES EXTRACTION
    bounding_boxes = bounding_boxes_extraction.get_bounding_boxes(foreground)
    print(f"== BOUNDING BOXES EXTRACTION END {t.get_time()}sec ==")

    #3a. TRACKING (optional)
    if param.tracking:
        tracking.setIDs(foreground, bounding_boxes)
        print(f"== TRACKING END {t.get_time()}sec ==")
    
    #3b. CELL COUNTING
    nb_cells = detect_cells.get_number_of_cells(frames, foreground, bounding_boxes, s, n)
    print(f"== DETECT CELLS END {t.get_time()}sec ==")

    #4. OUTPUT
    output.make_output(bounding_boxes, nb_cells)

    tiff_stack.close()

    #5. MEASURE (optional)
    if param.perf == True:
        return measure.compute_perf(s, n)
    
    return None, None, None, None, None
