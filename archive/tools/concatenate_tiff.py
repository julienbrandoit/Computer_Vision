import argparse
from PIL import Image

def concatenate_tiff(input_files, output_file):
    # Ouvrir le premier fichier pour obtenir ses propriétés
    first_image = Image.open(input_files[0])
    image_list = [first_image]

    # Ouvrir les autres fichiers et les ajouter à la liste
    for file_name in input_files[1:]:
        img = Image.open(file_name)
        image_list.append(img)

    # Enregistrer les images concaténées dans un seul fichier TIFF
    first_image.save(
        output_file,
        save_all=True,
        append_images=image_list[1:],
        resolution=first_image.info.get("dpi"),
    )

    # Fermer les images ouvertes
    for img in image_list:
        img.close()

    print(f"Les images ont été concaténées avec succès dans {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate TIFF images.")
    parser.add_argument("input_files", nargs="+", help="Input TIFF files to concatenate")
    parser.add_argument("output_file", help="Output concatenated TIFF file")

    args = parser.parse_args()
    
    concatenate_tiff(args.input_files, args.output_file)
