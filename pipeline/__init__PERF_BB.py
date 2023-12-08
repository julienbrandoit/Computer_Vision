import generate_model.BGS_model
import pipeline

import matplotlib.pyplot as plt
import time
import numpy as np
import param

if __name__ == "__main__":

    param.perf = True
    param.tracking = True

    ds = [[1,1], [2, 1], [3, 1], [3, 2], [3, 3], [4, 1], [6,1], [7,1], [8,1], [9,1], [10,1], [11,1], [12, 1]]
    #ds = [[1,1], [1,2], [1,3], [2,1], [2,2], [2,3], [3,1], [3,2], [3,3], [4,1], [4,2], [5,2], [5,3], [6,1], [6,2], [6,3], [7,1], [7,2], [7,3], [8,1], [8,2], [8,3], [9,2], [9,3], [10,1], [10,2], [10,3], [11,1], [11,3], [12, 1], [12, 2], [12, 3], [13,1], [13,2], [13,3], [14,2]]

    ds = [[1,2],[3,2]]
    scores = []

    iteration_labels = []  # List to store 's,n' labels
    for s, n in ds:
        print(f"s, n = {s} {n}:")

        generate_model.BGS_model.generate_model(s,n)
        score, _, _, _, _ = pipeline.start(s, n)
        iteration_labels.append(f"{s},{n}")
        scores.append(score)

    scores = np.array(scores)
    num_iterations = len(ds)

    plt.grid(True)
    plt.plot(iteration_labels, scores[:, 0], label='True Positives')
    plt.plot(iteration_labels, scores[:, 2], label='False Negatives')
    plt.plot(iteration_labels, scores[:, 1], label='False Positives')
    plt.legend()
    plt.show()
    plt.grid(True)
    plt.plot(iteration_labels, scores[:, 3], label='Mean Jaccard of true positives')
    plt.legend()
    plt.show()

    total_true_pos = np.mean(scores[:, 0])*100
    total_false_neg = np.mean(scores[:, 2])*100
    total_false_pos = np.mean(scores[:, 1])*100
    total_jaccard = np.mean(scores[:, 3]) * 100
    print("total true pos = ", total_true_pos, "total false neg = ", total_false_neg, "total false pos = ", total_false_pos, "total jaccard = ", total_jaccard)
    sd_true_pos = np.sqrt(np.var(scores[:, 0], ddof=0)) * 100
    sd_false_neg = np.sqrt(np.var(scores[:, 2], ddof=0)) * 100
    sd_false_pos = np.sqrt(np.var(scores[:, 1], ddof=0)) * 100
    sd_jaccard = np.sqrt(np.var(scores[:, 3], ddof=0)) * 100
    print("sd_true_pos = ", sd_true_pos, "sd_false_neg = ", sd_false_neg, "sd_false_pos = ", sd_false_pos, "sd_jaccard = ", sd_jaccard)

    
    # Tracking
    if param.tracking:
        bar_width_y1 = 0.6
        x = np.arange(len(iteration_labels))  # Generate x values
        plt.figure(figsize=(10, 6))
        plt.title(f"Accuracy of the tracking of the bounding boxes: mean accuracy = {np.mean(scores[:, 3])}")
        plt.bar(x, scores[:, 3], color='blue', width=bar_width_y1)
        plt.xticks(x, iteration_labels)  # Set x-axis labels
        plt.xlabel("Sequence")
        plt.xlabel("Accuracy")
        plt.show()
        print("tracking accuracy: mean = ", np.mean(scores[:, 3]))
        print("tracking accuracy; std = ", np.std(scores[:, 3]))
    
