import matplotlib.pyplot as plt
import numpy as np
import param
import json


def make_output(bounding_boxes, nb_cells):
    if param.output_json == True:
        result = {}

        for f in range(len(bounding_boxes)):
            key = f"frame_{f+1}"
            r = []

            for b in range(len(bounding_boxes[f])):
                x, _, w, _ = bounding_boxes[f][b][0:4]
                r.append((float(x) + float(w/2), nb_cells[f][b]))

            result[key] = r

        with open(param.output_json_path, 'w') as json_file:
            json.dump(result, json_file)
    else:
        pass

    if param.output_graph:
        nb_cells_flat = [nb for frame in nb_cells for nb in frame]

        # Plot the histogram
        fig1, axs1 = plt.subplots(1, 1, figsize=(7, 5))
        axs1.hist(nb_cells_flat, color='green', bins=20)
        axs1.set_xlabel('Number of Cells')
        axs1.set_ylabel('Number of Droplets')
        axs1.set_title('Histogram')
        axs1.grid(True)

        # Plot the horizontal boxplot
        fig2, axs2 = plt.subplots(1, 1, figsize=(15, 5))
        axs2.boxplot(nb_cells_flat, vert=False, showfliers=True, meanprops=dict(linewidth=2))
        axs2.set_yticklabels([])  # No y-ticks/labels
        axs2.set_xlabel('Number of Cells')
        axs2.set_ylabel('')
        axs2.set_title('')
        axs2.grid(True)
        # Add mean value text annotation
        mean_value = int(np.mean(nb_cells_flat))
        axs2.text(1, mean_value, f'Mean: {mean_value}', va='center', ha='right', bbox=dict(facecolor='white', alpha=0.5))

        if param.tracking:
            # Plot the scatter plot
            fig3, axs3 = plt.subplots(1, 1, figsize=(15, 5))
            data_dict = {}
            for f in range(len(nb_cells)):
                for b in range(len(nb_cells[f])):
                    id_val = bounding_boxes[f][b][-1]
                    if id_val not in data_dict:
                        data_dict[id_val] = []

                    data_dict[id_val].append(nb_cells[f][b])

            all_data = [val for sublist in data_dict.values()
                        for val in sublist]
            all_ids = [id_val for id_val, sublist in data_dict.items()
                       for _ in sublist]

            axs3.scatter(all_ids, all_data, color='green', alpha=0.8, s=7)
            axs3.scatter(data_dict.keys(), [np.mean(val) for val in data_dict.values()], marker='D', color='red')
            axs3.set_xlabel('ID')
            axs3.set_ylabel('Mean of Number of Cells')
            axs3.set_title('Scatter Plot')
            axs3.grid(True)

            for id_val in data_dict.keys():
                axs3.axvline(x=id_val, color='r', linestyle='--', linewidth=1)
        plt.show()
