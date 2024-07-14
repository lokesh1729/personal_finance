import csv


def rename_csv_columns(input_filename, output_filename, column_mapping):
    """
    Maps columns in an existing CSV file to a new CSV file based on the provided column mapping.

    Args:
        input_filename (str): The filename of the existing CSV file.
        output_filename (str): The filename of the new CSV file to be created.
        column_mapping (dict): A dictionary where the keys are the existing column names and the values are the new column names
    """
    # Read the existing CSV file
    with open(input_filename, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        # Create a new list of fieldnames based on the column_mapping
        new_fieldnames = list(filter(lambda item: item is not None, [column_mapping.get(field) for field in fieldnames]))

        # Write to a new CSV file with the updated column names
        with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()

            for row in reader:
                # Create a new row dictionary with updated column names
                new_row = {column_mapping.get(key): value for key, value in row.items() if column_mapping.get(key) is not None}
                writer.writerow(new_row)
