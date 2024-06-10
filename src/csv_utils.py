import csv


def convert_csv_to_json(file_path):
    csv_rows = []
    with open(file_path, encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True, quotechar='"')

        # Here we clean any Non-breaking spaces and convert to normal spacing. \xa0 converts to ' '
        for row in reader:
            temp_overwritable_dict = {}
            for key, value in row.items():
                cleaned_key = key.replace('\xa0', ' ')
                cleaned_value = value.replace('\xa0', ' ')
                temp_overwritable_dict.update({cleaned_key: cleaned_value})
            csv_rows.append(temp_overwritable_dict)

    if csv_rows == None or csv_rows == []:
        raise ValueError('Failed to convert CSV file to JSON. Exiting script.')
    return csv_rows
