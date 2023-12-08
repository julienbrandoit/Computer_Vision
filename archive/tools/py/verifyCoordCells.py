import pandas as pd
import re

# Charger les fichiers CSV
boxes_df = pd.read_csv('Results_boxes.csv')
cells_df = pd.read_csv('Results_cells.csv')

# Créer un dictionnaire pour stocker les données JSON
result = {}

# Itérer à travers les numéros de frame uniques
for frame_num in sorted(boxes_df['Slice'].unique()):
    frame_data = {"boxes": [], "cells": []}

    # Filtrer les lignes correspondant au numéro de frame actuel
    frame_boxes = boxes_df[boxes_df['Slice'] == frame_num]
    frame_cells = cells_df[cells_df['Slice'] == frame_num]

    # Remplir les données "boxes" à partir de boxes_df
    for _, row in frame_boxes.iterrows():
        box_entry = [row['BX'], row['BY'],
                     row['Width'], row['Height'], row['Group']]
        frame_data["boxes"].append(box_entry)

    # Remplir les données "cells" à partir de cells_df
    for _, row in frame_cells.iterrows():
        label = row['Label']
        # Extraire l'ID à partir du champ label
        match = re.search(r'\d+_(\d+)', label)
        id_value = int(match.group(1))
        cell_entry = [row['X'], row['Y'], id_value]
        frame_data["cells"].append(cell_entry)

    # Ajouter les données au résultat final
    result[frame_num] = frame_data

for frame_id, val in result.items():
    if frame_id > 30:
        continue

    for boxe in val["boxes"]:
        BX, BY, W, H = boxe[0:4]
        for cell in val["cells"]:
            if boxe[-1] == cell[-1]:
                X, Y = cell[0:2]
                if not(BX <= X <= BX+W) or not(BY <= Y <= BY+H):
                    print(f"Attention : frame {frame_id} | boxe {boxe[-1]} | cell outside bounding boxe : X = {X}, Y = {Y}")

print("Recherche terminée.")
