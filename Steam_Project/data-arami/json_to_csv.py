import json
import csv
import os

def extract_list(data):
    # Case 1: data is already a list
    if isinstance(data, list):
        return data
    # Case 2: dict with one top-level key whose value is a list
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                return value
            elif isinstance(value, dict):
                # Try one more level deep
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):
                        return subvalue
    raise ValueError("Could not find a list of records in the JSON structure.")

# Input JSON file name
input_filename = 'game_names_id.json'
base_name = os.path.splitext(input_filename)[0]
output_filename = f'{base_name}.csv'

# Load JSON data
with open(input_filename, 'r', encoding='utf-8') as json_file:
    raw_data = json.load(json_file)

# Extract list of records
data = extract_list(raw_data)

# Write to CSV
with open(output_filename, 'w', newline='', encoding='utf-8') as csv_file:
    headers = data[0].keys() if data else []
    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)

print(f"CSV file '{output_filename}' created successfully.")
