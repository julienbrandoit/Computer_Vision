import json

def verifier_fichier_json(json_file):
    try:
        with open(json_file, 'r') as fichier:
            data = json.load(fichier)

            if not isinstance(data, dict):
                raise ValueError("Le fichier JSON ne contient pas un dictionnaire")

            for key, item in data.items():
                if not isinstance(item, dict):
                    raise ValueError(f"La valeur associée à la clé '{key}' n'est pas un dictionnaire")

                parts = key.split('_')

                if len(parts) != 4:
                    raise ValueError(f"La clé '{key}' ne suit pas le format X_Y_frame_Z")

                X, Y, frame, Z = parts

                if not (X.isdigit() and Y.isdigit() and Z.isdigit() and 1 <= int(Z) <= 50):
                    raise ValueError(f"La clé '{key}' ne suit pas le format X_Y_frame_Z attendu")
                else:
                    print("X, Y,Z : ", X, Y, Z)

                if 'boxes' not in item or 'cells' not in item:
                    raise ValueError(f"La valeur associée à la clé '{key}' ne contient pas 'boxes' et 'cells' comme sous-clés")

                for sub_key in ['boxes', 'cells']:
                    if not isinstance(item[sub_key], list):
                        raise ValueError(f"La valeur associée à la clé '{key}' contenant '{sub_key}' n'est pas une liste")

                    for j, sub_item in enumerate(item[sub_key], start=1):
                        if sub_key == 'boxes' and len(sub_item) != 5:
                            raise ValueError(f"L'élément {j} de '{sub_key}' associé à la clé '{key}' n'a pas la taille attendue (5)")
                        if sub_key == 'cells' and len(sub_item) != 3:
                            raise ValueError(f"L'élément {j} de '{sub_key}' associé à la clé '{key}' n'a pas la taille attendue (3)")

        print("Le fichier JSON est valide")

    except FileNotFoundError:
        print("Le fichier JSON n'a pas été trouvé.")
    except json.JSONDecodeError:
        print("Erreur de décodage JSON")
    except ValueError as e:
        print(f"Erreur de validation: {str(e)}")

# Utilisation du code en passant le nom du fichier JSON
fichier_json = "json/3-1.json"
verifier_fichier_json(fichier_json)
