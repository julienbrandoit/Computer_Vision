import generate_model.BGS_model
import pipeline

import numpy as np
import matplotlib.pyplot as plt
import time
import numpy as np
import param
from matplotlib.cm import ScalarMappable

if __name__ == "__main__":

    param.perf = True
        
    ds = [[1,1], [1,2], [2,1], [2,2], [2,3], [3,1], [3,2], [3,3], [4,1], [4,2], [5,2], [5,3], [6,1], [6,2], [6,3], [7,1], [7,3], [8,1], [8,2], [8,3], [9,2], [9,3], [10,1], [10,2], [10,3], [11,1], [11,3], [12, 1], [12, 2], [12, 3], [13,1], [13,2], [13,3], [14,2]]

    comp_cells = []
    real_cells = []
    diff_cells = []

    diff_cells_plot = []

    comp_dist = []
    rand_dist = []
    norm_dist = []

    norm_dist_plot = []
    label = []

    start_time = time.time()
    for s, n in ds:
        print(f"s, n = {s} {n}:")
        generate_model.BGS_model.generate_model(s,n)
        _, c, d, b, _ = pipeline.start(s, n)

        comp_cells += c[0]
        real_cells += c[1]
        diff_cells += b[0]

        diff_cells_plot.append(np.mean(b[0]))

        comp_dist += d[0]
        rand_dist += d[1]
        norm_dist += b[1]

        norm_dist_plot.append(np.mean(b[1]))
        label.append(f"{s}-{n}")

    print(f"difference of cells : {np.mean(diff_cells)*100}% +- {np.std(diff_cells)*100}%")
    print(f"Computed #cells per boxe : {np.mean(comp_cells)} +- {np.std(comp_cells)}")
    print(f"Real #cells per boxe : {np.mean(real_cells)} +- {np.std(real_cells)}")
    print()
    print(f"Computed vs rand : {np.mean(norm_dist)} +- {np.std(norm_dist)}")
    print(f"Computed mean distance : {np.mean(comp_dist)} +- {np.std(comp_dist)}")
    print(f"Random mean distance : {np.mean(rand_dist)} +- {np.std(rand_dist)}")

    end_time = time.time()

    print("TIME : ", end_time - start_time, "s; FPS : ", (len(ds)*100)/(end_time - start_time), "fps")

    bar_width_y1 = 0.6
    x = np.arange(0, len(ds), 1)

    plt.figure(figsize=(15,5))
    plt.bar(x, diff_cells_plot, bar_width_y1)
    plt.tight_layout()
    plt.xticks(x, label) 
    plt.show()

    plt.figure(figsize=(15,5))
    plt.bar(x, norm_dist_plot, bar_width_y1)
    plt.tight_layout()
    plt.xticks(x, label) 
    plt.show()

    exit()