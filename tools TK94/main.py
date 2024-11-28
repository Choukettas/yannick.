import argparse
import json
import os
import csv
from datetime import datetime

def decode_timestamp(timestamp):
    """Convertit un timestamp UNIX en date lisible"""
    try:
        return datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "N/A"

def clean_newlines(value):
    """Remplace les \n par des espaces dans une chaîne de caractères"""
    if isinstance(value, str):
        return value.replace("\n", " ")
    return value

def extract_info_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        extracted_data = []
        max_characteristics = 0  # Pour déterminer le nombre maximal de caractéristiques

        for record in data:
            key_data = clean_newlines(record.get("key", ""))
            value_data = json.loads(record.get("value", "{}"))
            attributes = value_data.get("attributes", [])
            characteristics = value_data.get("characteristics", [])

            # Calculer le nombre maximal de caractéristiques
            max_characteristics = max(max_characteristics, len(characteristics))

            # Informations de base
            info = {
                "date": decode_timestamp(record.get("timestamp", "")),
                "FullName": key_data,
                "Type": clean_newlines(value_data.get("type", "")),
                "name": clean_newlines(value_data.get("name", "")),
                "revision": clean_newlines(value_data.get("revision", "")),
                "maturite": clean_newlines(next((attr["Value"][0] for attr in attributes if attr["name"] == "current"), "")),
                "projet": clean_newlines(next((attr["Value"][0] for attr in attributes if attr["name"] == "project"), "")),
                "ads": clean_newlines(value_data.get("ads", {}).get("name", "")),
                "libelle": clean_newlines(value_data.get("label", "")),
                "IND": clean_newlines(value_data.get("ind", {}).get("name", "")),
                "BIB_Correction": next((int(attr["Value"][0]) for attr in attributes if attr["name"] == "BIB_Correction"), ""),
                "BIB_Confidentiality": clean_newlines(next((attr["Value"][0] for attr in attributes if attr["name"] == "BIB_Confidentiality"), ""))
            }

            # Ajouter les caractéristiques
            for i, characteristic in enumerate(characteristics, start=1):
                info[f"characteristic_{i}_id"] = clean_newlines(characteristic.get("characteristicId", ""))
                info[f"characteristic_{i}_identifier"] = clean_newlines(characteristic.get("identifier", ""))
                info[f"characteristic_{i}_category"] = clean_newlines(characteristic.get("characteristicCategory", ""))

            extracted_data.append(info)

        return extracted_data, max_characteristics

    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return None, 0

def save_to_csv(data, max_characteristics, input_file):
    output_file = os.path.splitext(input_file)[0] + ".csv"

    # Générer les noms de colonnes dynamiquement
    fieldnames = list(data[0].keys())
    for i in range(1, max_characteristics + 1):
        fieldnames.extend([
            f"characteristic_{i}_id",
            f"characteristic_{i}_identifier",
            f"characteristic_{i}_category"
        ])

    # Écrire dans le fichier CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            # Compléter les colonnes manquantes avec ""
            for i in range(1, max_characteristics + 1):
                row.setdefault(f"characteristic_{i}_id", "")
                row.setdefault(f"characteristic_{i}_identifier", "")
                row.setdefault(f"characteristic_{i}_category", "")
            writer.writerow(row)

    print(f"Résultats enregistrés dans : {output_file}")

def main(args):
    file_path = args.path

    if not os.path.isfile(file_path):
        print("Le fichier spécifié n'existe pas. Vérifiez le chemin.")
        return

    data, max_characteristics = extract_info_from_file(file_path)
    if data:
        save_to_csv(data, max_characteristics, file_path)
    else:
        print("Aucune donnée extraite.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Chemin du fichier JSON", type=str)
    args = parser.parse_args()
    main(args)