import json
import numpy as np
import matplotlib.pyplot as plt

# Charger le fichier JSON
boxes = []
for s in range(1, 15):
    for n in range(1, 4):
        boxes_n = []
        for i in range(0, 30):
            boxes_n.append([])

        if s == 4 and n == 3:
            continue
        if s == 14 and n == 1:
            continue
        if s == 11 and n == 2:
            continue
        if s == 5 and n == 1:
            continue
        if s == 15 and n == 1:
            continue
        if s == 9 and n == 1:
            continue
        if s == 14 and n == 1:
            continue

        if s == 14 and n == 3:
            continue
        if s == 15 and (n == 2 or n == 3):
            continue

        data = 0
        with open(f'all_json/{s}_{n}.json', 'r') as f:
            data = json.load(f)
            for f in range(0, 50):
                frame_data = data[f"{s}_{n}_frame_{f+1}"]
                boxes_f = frame_data["boxes"]
                for b in boxes_f:
                    id = int(b[4])
                    if id == 0:
                        continue
                    boxes_n[id-1].append([b[0], b[1], b[2], b[3]])
        
        for b in boxes_n:
            if len(b) == 0:
                continue
            boxes.append(b)

x = []
y = []

for i in range(0, len(boxes)):
    x.append(i)
    y.append(len(boxes[i]))

#plt.plot(x,y)
#plt.show()

speed_x = []
speed_y = []
speed = []
for id, b in enumerate(boxes):
    if len(b) == 1:
        continue

    for j in range(0, len(b)-1):
        c = [b[j][0], b[j][1]]
        n = [b[j+1][0], b[j+1][1]]
        v = [n[0]-c[0], n[1] - c[1]]
        speed_x.append(v[0])
        speed_y.append(v[1])
        s = np.linalg.norm(v)
        speed.append(s)

radius_x = []
radius_y = []
for id, b in enumerate(boxes):
    for j in range(0, len(b)):
        radius_x.append(b[j][2]/2)
        radius_y.append(b[j][3]/2)
"""
x = []
for i in range(0, len(speed)):
    x.append(i)

#plt.plot(x, speed_x, speed_y)
plt.plot(x, speed_x, speed_y)
plt.show()
"""
def remove_outliers(data):
    # Calculate the first quartile (Q1), third quartile (Q3), and interquartile range (IQR)
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    # Define the lower and upper bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter the data to keep only values within the bounds
    filtered_data = [value for value in data if lower_bound <= value <= upper_bound]

    return filtered_data

speed_filtered = remove_outliers(speed)
speed_filtered_x = remove_outliers(speed_x)
speed_filtered_y = remove_outliers(speed_y)
"""
x = []
for i in range(0, len(speed_filtered)):
    x.append(i)

plt.plot(x, speed_filtered, speed)
plt.show()
"""
"""
x = []
for i in range(0, len(speed_filtered_x)):
    x.append(i)

plt.plot(x, speed_filtered_x)
plt.show()
"""
"""
x = []
for i in range(0, len(speed_filtered_y)):
    x.append(i)

plt.plot(x, speed_filtered_y, speed_y)
plt.show()
"""
mean_speed = np.mean(speed_filtered)
mean_speed_x = np.mean(speed_filtered_x)
sigma_speed_x = np.sqrt(np.var(speed_filtered_x))
mean_speed_y = np.mean(speed_filtered_y)
sigma_speed_y = np.sqrt(np.var(speed_filtered_y))
print("mean speed : ", mean_speed, "pixels/frame")
print("mean speed x : ", mean_speed_x, "pixels/frame, sigma : ", sigma_speed_x)
print("mean speed y : ", mean_speed_y, "pixels/frame, sigma : ", sigma_speed_y)


radius_x_filtered = remove_outliers(radius_x)
radius_y_filtered = remove_outliers(radius_y)
"""
x = []
for i in range(0, len(radius_x_filtered)):
    x.append(i)

plt.plot(x, radius_x_filtered)
plt.show()
"""
"""
x = []
for i in range(0, len(radius_y_filtered)):
    x.append(i)

plt.plot(x, radius_y_filtered)
plt.show()
"""
mean_radius_x = np.mean(radius_x_filtered)
mean_radius_y = np.mean(radius_y_filtered)
mean_radius = np.mean(radius_x_filtered + radius_y_filtered)
sigma_radius = np.sqrt(np.var(radius_x_filtered + radius_y_filtered))
print("mean radius : ", mean_radius_x, "pixels, sigma : ", sigma_radius)
print("mean radius x : ", mean_radius_y, "pixels")
print("mean radius y : ", mean_radius, "pixels")
