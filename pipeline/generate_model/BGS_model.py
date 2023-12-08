import cv2
import tifffile as tf
import pickle
import param

def generate_model(s,n):

    # print("== BGS generate model ==")
        
    bg_subtractor = cv2.createBackgroundSubtractorMOG2()
    
    for i in range(param.bgs_learning_time):
        input_path = param.input_path.format(s, n)
        tiff_stack = tf.TiffFile(input_path).asarray()

        if param.print_frame:
            print(f"BGS model {i+1}/{param.bgs_learning_time}")

        for frame in tiff_stack:
            resized_frame = cv2.resize(frame, (int(frame.shape[1] * param.bgs_scaling_factor), int(frame.shape[0] * param.bgs_scaling_factor)))
            bg_subtractor.apply(resized_frame)

    background_image = cv2.resize(bg_subtractor.getBackgroundImage(), (tiff_stack[0].shape[1], tiff_stack[0].shape[0]))
    cv2.imwrite(param.background_image_path, background_image)    
    print("== BGS generate model END ==")