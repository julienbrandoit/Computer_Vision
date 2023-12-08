import pandas as pd
import json
import re

# Variables pour groupid et studentid
groupid = "3"
studentid = "2"

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

    # Construire la clé JSON (groupid_studentid_frameX)
    json_key = f"{groupid}_{studentid}_frame_{frame_num}"

    # Ajouter les données au résultat final
    result[json_key] = frame_data

for key, val in result.items():
    frame_id = int(re.search(r"frame_(\d+)", key).group(1))
    if frame_id > 30:
        continue

    for boxe in val["boxes"]:
        BX, BY, W, H = boxe[0:4]
        for cell in val["cells"]:
            if boxe[-1] == cell[-1]:
                X, Y = cell[0:2]
                if not(BX <= X <= BX+W) or not(BY <= Y <= BY+H):
                    print(f"Attention : frame {frame_id} | boxe {boxe[-1]} | cell outside bounding boxe : X = {X}, Y = {Y}")

# Convertir le dictionnaire en format JSON
json_output = json.dumps(result, indent=4)

# Écrire le JSON dans un fichier de sortie
with open('output.json', 'w') as json_file:
    json_file.write(json_output)

print("Conversion terminée. Les données ont été enregistrées dans 'output.json'.")
