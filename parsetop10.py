import os
import pandas as pd
import csv
import subprocess

counter = 1

# Load the CSV file
csv_path = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/top_10_mutations/imaging/top_10_mutations.csv'
mutations_df = pd.read_csv(csv_path)

# Load the original PIT CSV file
original_pit_csv_path = '/Users/matt/Downloads/commons-imaging-1.0.0-alpha5-src/target/pit-reports/mutations.csv'
original_pit_df = pd.read_csv(original_pit_csv_path)

# Define the base directory where the source files are located
base_src_dir = '/Users/matt/Downloads/commons-imaging-1.0.0-alpha5-src/src/main/java/'

# Initialize the counter for missing files
missing_files_counter = 0


def get_line_numbers(df, method_name, mutator_name):
    # Filter the DataFrame based on the given method name and mutator name
    filtered_df = df[(df.iloc[:, 3] == method_name) & (df.iloc[:, 2] == mutator_name)]

    # Get the list of line numbers from the filtered DataFrame
    line_numbers = filtered_df.iloc[:, 4].tolist()

    return line_numbers


# Function to locate the source file for a given class
def find_source_file(class_name):
    # Remove everything from the $ character onwards if it exists
    class_name = class_name.split('$')[0]
    # Convert the class name to a file path
    file_path = class_name.replace('.', '/') + '.java'
    # Construct the full path
    full_path = os.path.join(base_src_dir, file_path)
    # print(full_path)
    return full_path if os.path.exists(full_path) else None


def find_method_lines_and_content(source_file, method_name, line_numbers):
    with open(source_file, 'r') as file:
        lines = file.readlines()

    start_line = None
    end_line = None
    method_content = []
    inside_method = False
    braces_counter = 0
    inside_multiline_comment = False

    for i, line in enumerate(lines):

        stripped_line = line.strip()

        # Check for the start and end of multi-line comments
        if stripped_line.startswith("/*") and not inside_method:
            inside_multiline_comment = True
        if inside_multiline_comment and stripped_line.endswith("*/"):
            inside_multiline_comment = False
            continue

        # Ignore single-line comments and lines inside multi-line comments
        if (stripped_line.startswith("//") or inside_multiline_comment or "try" in stripped_line) and not inside_method:
            continue

        if method_name in line and not inside_multiline_comment and '(' in line and ')' in line and '{' in line:
            start_line = i
            inside_method = True
            braces_counter = 1
            method_content.append(line)
            continue

        if inside_method:
            method_content.append(line)
            if '{' in line:
                braces_counter += 1
            if '}' in line:
                braces_counter -= 1
                if braces_counter == 0:
                    end_line = i + 1
                    break

    # Check if any of the given line numbers are within the method's lines
    if start_line is not None and end_line is not None:
        for ln in line_numbers:
            if start_line < ln <= end_line:
                return start_line, end_line, method_content

    return None, None, None


# Output CSV file
output_csv_path = 'methods_with_lines.csv'

# Prepare to write to the CSV file
with open(output_csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['mutator', 'class', 'method_name', 'method_lines', 'start_line', 'end_line']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()

    for index, row in mutations_df.iterrows():
        mutator = row['Top 10 Mutators']
        classes = row['Classes Applied To'].split(', ')
        methods = row['Methods Applied To'].split(', ')
        # line_numbers = [int(ln) for ln in row['Line Numbers'].split(', ')]

        for class_name in classes:
            source_file = find_source_file(class_name)
            if source_file:
                for method_name in methods:
                    line_numbers = get_line_numbers(original_pit_df, method_name, mutator)
                    start_line, end_line, method_content = find_method_lines_and_content(source_file, method_name, line_numbers)
                    if start_line is not None and end_line is not None:
                        method_lines = "".join(method_content)
                        writer.writerow({
                            'mutator': mutator,
                            'class': class_name,
                            'method_name': method_name,
                            'method_lines': method_lines,
                            'start_line': start_line,
                            'end_line': end_line
                        })
                        # counter
                        print(f"found{counter}")
                        counter += 1
                    else:
                        #print(f"Method {method_name} not found in {class_name}")
                        missing_files_counter += 1
            else:
                print(f"Source file not found for class {class_name}")
                # Increment the counter if the file is not found
                missing_files_counter += 1

print(f"Total missing files: {missing_files_counter}")