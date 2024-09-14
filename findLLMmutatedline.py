import pandas as pd
import difflib

def find_differences_with_difflib_ignore_whitespace(original_method: str, different_method: str, start_line: int):
    # Split the methods into lines and strip whitespace
    original_lines = [line.strip() for line in original_method.splitlines()]
    different_lines = [line.strip() for line in different_method.splitlines()]

    # Use difflib to find the differences
    differ = difflib.Differ()
    diff = list(differ.compare(original_lines, different_lines))

    differing_lines = set()  # Use a set to ensure uniqueness
    original_index = 0
    different_index = 0

    for line in diff:
        if line.startswith('  '):  # No difference, move both indices forward
            original_index += 1
            different_index += 1
        elif line.startswith('- '):  # Line removed from original, move original_index forward
            original_index += 1
        elif line.startswith('+ '):  # Line added in different, move different_index forward
            different_index += 1
        elif line.startswith('? '):  # Marker for close lines, skip
            continue
        if line.startswith('- ') or line.startswith('+ '):
            # Check if the line content really differs (ignoring possible '?' markers)
            if (line.startswith('- ') and original_lines[original_index - 1] != different_lines[different_index - 1]):
                differing_lines.add(original_index)  # Add to set for uniqueness
            elif (line.startswith('+ ') and original_lines[original_index - 1] != different_lines[different_index - 1]):
                differing_lines.add(different_index)  # Add to set for uniqueness

    # Adjust line numbers by adding them to start_line + 1
    adjusted_lines = [line + start_line for line in sorted(differing_lines)]

    return adjusted_lines

def add_mutation_line_numbers_to_csv(input_csv: str, output_csv: str):
    # Read the CSV file
    df = pd.read_csv(input_csv)

    # Apply the difference logic to each row
    df['llm_mutation_line_number'] = df.apply(
        lambda row: find_differences_with_difflib_ignore_whitespace(
            row['original_method'], row['mutated_method'], row['start_line']
        ),
        axis=1
    )

    # Convert the list of differing line numbers to a string for easier CSV storage
    df['llm_mutation_line_number'] = df['llm_mutation_line_number'].apply(lambda x: ','.join(map(str, x)))

    # Save the updated DataFrame back to a new CSV file
    df.to_csv(output_csv, index=False)

# Example usage:
input_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/combined_mutation_results.csv'
output_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/combined_mutation_results_with_line.csv'
add_mutation_line_numbers_to_csv(input_csv, output_csv)