import os
import sys
import csv
import yaml

def convert(input_file, output_file):
    if not os.path.isfile(input_file):
        print(f'Filepath "{input_file}" not found! Please provide a valid path.')
        exit(1)

    keyword_dict = {}

    # Read csv file
    with open(input_file, mode='r') as file:
        reader = csv.reader(file)
        # Skip header row
        next(reader)
        for row in reader:
            keyword_dict[row[0]] = [w for w in row[1:] if w]

    # Export as yaml; overwrite existing files
    with open(output_file, mode='w') as file:
        yaml.dump(keyword_dict, file, allow_unicode=True, indent=4)

    print("File converted successfully.")


def main():
    if len(sys.argv) != 3:
        print("Usage: python convert_csv2yml <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert(input_file, output_file)

if __name__ == "__main__":
    main()
