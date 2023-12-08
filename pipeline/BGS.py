import cv2
import tifffile as tf
import param
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_frame(frame, bg_model):
    channel = frame.shape[2] if len(frame.shape) == 3 else 1

    if channel == 3:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    fg_mask = cv2.absdiff(frame, bg_model)
    fg_mask = cv2.medianBlur(fg_mask, 5, fg_mask)
    fg_mask = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)[1]

    return frame, fg_mask

def BGS(frames_array):
    if param.output_BGS == True:
        output_path = param.output_BGS_tif
        output_tiff_stack = tf.TiffWriter(output_path)

    bg_model = cv2.imread(param.background_image_path)
    bg_model = cv2.cvtColor(bg_model, cv2.COLOR_RGB2GRAY)
    
    frames = [None]*len(frames_array)
    foreground_masks = [None]*len(frames_array)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_frame, frame, bg_model): i for i, frame in enumerate(frames_array)}

        for future in as_completed(futures):
            index = futures[future]
            frame, fg_mask = future.result()
            foreground_masks[index] = fg_mask
            frames[index] = frame

            if param.print_frame:
                print(f"- BGS : frame {index}")

    if param.output_BGS == True:
        for fg_mask in foreground_masks:
            output_tiff_stack.save(fg_mask)
        output_tiff_stack.close()

    return frames, foreground_masks
