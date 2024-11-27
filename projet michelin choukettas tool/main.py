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

def extract_info_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        extracted_data = []
        for record in data:
            key_data = record.get("key", "N/A")
            value_data = json.loads(record.get("value", "{}"))
            attributes = value_data.get("attributes", [])

            info = {
                "date": decode_timestamp(record.get("timestamp", "N/A")),
                "FullName": key_data,
                "Type": value_data.get("type", "N/A"),
                "name": value_data.get("name", "N/A"),
                "revision": value_data.get("revision", "N/A"),
                "maturite": next((attr["Value"][0] for attr in attributes if attr["name"] == "current"), "N/A"),
                "projet": next((attr["Value"][0] for attr in attributes if attr["name"] == "project"), "N/A"),
                "ads": value_data.get("ads", {}).get("name", "N/A"),
                "libelle": value_data.get("label", "N/A"),
                "IND": value_data.get("ind", {}).get("name", "N/A"),
                "BIB_Correction": next((int(attr["Value"][0]) for attr in attributes if attr["name"] == "BIB_Correction"), 0),
                "BIB_Confidentiality": next((attr["Value"][0] for attr in attributes if attr["name"] == "BIB_Confidentiality"), "N/A")
            }

            extracted_data.append(info)

        return extracted_data

    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return None

def save_to_csv(data, input_file):
    output_file = os.path.splitext(input_file)[0] + ".csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    print(f"Résultats enregistrés dans : {output_file}")

def main(args):
    file_path = args.path

    if not os.path.isfile(file_path):
        print("Le fichier spécifié n'existe pas. Vérifiez le chemin.")
        return

    data = extract_info_from_file(file_path)
    if data:
        save_to_csv(data, file_path)
    else:
        print("Aucune donnée extraite.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path",help="chemin de json",type=str)
    args = parser.parse_args()
    main(args)
    
