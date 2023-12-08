import numpy as np

all_json_path = "all_json/{}_{}.json"
input_path = "in/{}-{}.tif"
output_json_path = "output/output.json"


output_json = True      # Activate/Deacitve the output of results in a json file

tracking = False        # Activate/Deacitve tracking
perf = True             # Activate/Deacitve metrics computation

print_frame = False     # Desplay which frame has been processed


### output json ###
bb_json_path = "output/perf/bb.json"
tr_json_path = "output/perf/tr.json"
dc_json_path = "output/perf/dc.json"

output_graph = False

### Background substraction ###
output_BGS = False      # Activate/Deacitve the output of BGS as a tiff file

bgs_scaling_factor = 0.2
bgs_learning_time = 5
background_image_path = "model/BGS_model.png"
output_BGS_tif = "output/BGS-output.tif"


### Bounding boxe ###
output_BB = False       # Activate/Deacitve the output of BB as a tiff file
output_BB_tif = "output/BB-output.tif"

scaling_factor = 0.35
mean_radius = 297 * scaling_factor
sigma_radius = 7 * scaling_factor
min_radius = mean_radius-5*sigma_radius
max_radius = mean_radius+5*sigma_radius
min_perim = 2*np.pi*min_radius
max_perim = 2*np.pi*max_radius
edge_margin = 0
scale_kernel = 0.85
dilate_loss = 0.95
border_size = 5


### Tracking ###
output_tracking = False # Activate/Deacitve the output of tracking as a tiff file
output_tracking_tif = "output/TR-output.tif"


### Cells detection ###
output_DC = False       # Activate/Deacitve the output of DC as a tiff file
output_DC_tif = "output/DC-output.tif"

# If you change the scale factor, change the other parameters with the corresponding values
dc_scale = 0.5           # 1  | 0.5
dc_hough_param1 = 50     # 50 | 50
dc_hough_param2 = 18     # 26 | 18
dc_kernel_size = 4       # 6  | 4
dc_bifilter_size = 5     # 9  | 5
dc_hough_min_dists = int(15 * dc_scale)
dc_hough_min_r = int(5 * dc_scale)
dc_hough_max_r = int(35 * dc_scale)


# Mean values based on all_json, found with compute_stat
mean_x = 284.02
mean_y = -1.60
sigma_x = 29.77
sigma_y = 9.12
mean_r = 297