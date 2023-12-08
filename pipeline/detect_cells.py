import concurrent.futures
import tifffile as tf
import numpy as np
import param
import json
import cv2


def output_to_json(cells, boxes):
    output = {'cells': cells, 'boxes': boxes}

    with open(param.dc_json_path, 'w') as json_file:
        json.dump(output, json_file)


def realign_circle(boxes, circles):
    output = []

    for i, boxe in enumerate(boxes):
        X, Y = boxe[0:2]
        output.append([[int(circles[i][j][0]*(1/param.dc_scale) + X), int(circles[i]
                      [j][1]*(1/param.dc_scale) + Y)] for j in range(len(circles[i]))])

    return output


def extract_bulle(frame, boxes):
    bulle = []

    for i in range(len(boxes)):
        X, Y, W, H = boxes[i][0:4]
        tmp = frame[Y:Y+H, X:X+W]

        if param.dc_scale != 1:
            bulle.append(cv2.resize(
                tmp, (0, 0), fx=param.dc_scale, fy=param.dc_scale))
        else:
            bulle.append(tmp)

    return bulle


def include_bulle(frame, bulles, boxes):
    output = np.copy(frame)
    output = cv2.cvtColor(output, cv2.COLOR_GRAY2RGB)

    for i in range(len(boxes)):
        tmp = bulles[i]
        if param.dc_scale != 1:
            tmp = cv2.resize(bulles[i], (0, 0), fx=1/param.dc_scale, fy=1/param.dc_scale)

        X, Y = boxes[i][0:2]
        clamp_x = len(tmp[0])+len(frame[0])-(X+len(tmp[0])) if X + len(tmp[0]) >= len(frame[0]) else len(tmp[0])
        clamp_y = len(tmp)+len(frame)-(Y+len(tmp)) if Y + len(tmp) >= len(frame) else len(tmp)

        output[Y:Y+len(tmp), X:X+len(tmp[0])] = tmp[0:clamp_y, 0:clamp_x]

    return output


def find_circle(bulles_BGS, bulles_real):
    circle_real = []
    nb_cells = []
    pos_circle = []

    for i, bulle in enumerate(bulles_BGS):
        circles = cv2.HoughCircles(
            bulle,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=param.dc_hough_min_dists,
            param1=param.dc_hough_param1,
            param2=param.dc_hough_param2,
            minRadius=param.dc_hough_min_r,
            maxRadius=param.dc_hough_max_r
        )

        if param.output_DC and circles is not None:
            result_real = cv2.cvtColor(bulles_real[i], cv2.COLOR_GRAY2RGB)
            circles = np.uint16(np.around(circles))

            cv2.rectangle(result_real, (2, 2), (len(bulle[0])-4, len(bulle)-4), (255, 0, 0), int(3 * param.dc_scale)+1)
            for i in circles[0, :]:
                cv2.circle(result_real, (i[0], i[1]), 2, (0, 0, 255), int(3 * param.dc_scale)+1)

            circle_real.append(result_real)

        if circles is not None:
            nb_cells.append(len(circles[0, :]))
            pos_circle.append(circles[0, :, 0:2])

    return circle_real, nb_cells, pos_circle


def process_frame(f, frame, frame_BGS, boxes_i):

    bulles_BGS = extract_bulle(frame_BGS, boxes_i)
    bulles_real = extract_bulle(frame, boxes_i)

    size = param.dc_kernel_size
    kernel = np.ones((size, size), np.uint8)

    results = [None] * len(bulles_BGS)
    for j in range(len(bulles_BGS)):
        # Improve BGS
        results[j] = cv2.morphologyEx(bulles_BGS[j], cv2.MORPH_CLOSE, kernel)
        results[j] = cv2.morphologyEx(results[j], cv2.MORPH_DILATE, kernel)

        # Merge BGS with real image
        results[j] = cv2.bitwise_and(bulles_real[j], bulles_real[j], mask=results[j])
        results[j] = cv2.bilateralFilter(results[j], param.dc_bifilter_size, 75, 75)

    circle_real, nb_cells, pos_circle = find_circle(results, bulles_real)

    circles = realign_circle(boxes_i, pos_circle) if param.perf else None
    output_frame = include_bulle(
        frame, circle_real, boxes_i) if param.output_DC else None

    return nb_cells, circles, output_frame


def get_number_of_cells(frames, frames_BGS, boxes, s, n):
    full_nb_cells = [[] for i in range(len(frames))]
    full_circle_pos = [[] for i in range(len(frames))]
    output_frame = [None] * len(frames)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_frame, f, frames[f], frames_BGS[f], boxes[f]): (
            f, frames[f], boxes[f]) for f in range(len(frames))}

        for future in concurrent.futures.as_completed(futures):
            f, frame, boxes_i = futures[future]

            if param.print_frame:
                print(f"- DC : frame {f}")

            try:
                nb_cells, circle_pos, frame_out = future.result()
                full_nb_cells[f] = nb_cells
                output_frame[f] = frame_out

                if param.perf:
                    full_circle_pos[f] += circle_pos

            except Exception as e:
                print(f"Error processing frame {f}: {e}")
                full_nb_cells[f] = [0] * len(boxes_i)
                if param.output_DC:
                    output_frame[f] = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

    if param.perf:
        output_to_json(full_circle_pos[0:30], boxes[0:30])

    if param.output_DC:
        output_tiff_stack = tf.TiffWriter(param.output_DC_tif)
        for i in output_frame:
            output_tiff_stack.save(i)
        output_tiff_stack.close()

    return full_nb_cells
