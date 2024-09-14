import pandas as pd
import random

def compare_mutations(llm_csv, pit_csv, output_csv):
    # Load the CSV files
    llm_df = pd.read_csv(llm_csv)
    pit_df = pd.read_csv(pit_csv)

    # Initialize a list to store the matched results
    matched_results = []

    # Clean PIT class names and method names before comparison
    pit_df_clean = pit_df.copy()
    pit_df_clean.iloc[:, 1] = pit_df_clean.iloc[:, 1].apply(lambda x: x.split('$')[0])  # Clean class names
    pit_df_clean.iloc[:, 3] = pit_df_clean.iloc[:, 3].apply(lambda x: x.split('$')[0])  # Clean method names
    # Iterate over each row in the LLM DataFrame
    for _, llm_row in llm_df.iterrows():
        # Extract values from the LLM row
        class_name = llm_row['class_name'].split('$')[0]  # Split by $ and take the first part
        mutator_type = llm_row['mutator_type']
        original_method = llm_row['original_method']
        llm_lines = set(map(int, map(float, str(llm_row['llm_mutation_line_number']).split(',')))) if pd.notna(
            llm_row['llm_mutation_line_number']) and llm_row['llm_mutation_line_number'] else set()
        llm_killed = 'Killed' if llm_row['mutation_score'] == 1 else 'Survived'

        # Filter PIT rows based on class_name, mutator_type, and method name
        pit_match = pit_df_clean[
            (pit_df_clean.iloc[:, 1] == class_name) &  # 2nd column for class_name
            (pit_df_clean.iloc[:, 2] == mutator_type) &  # 3rd column for mutator_type
            (pit_df_clean.iloc[:, 3].apply(lambda x: x in original_method)) &  # 4th column for method name
            (pit_df_clean.iloc[:, 4].astype(int).isin(llm_lines))  # 5th column for line number
        ].head(1)  # Select only the first matching row

        # If a match is found, process it
        if not pit_match.empty:
            pit_row = pit_match.iloc[0]
            pit_killed = 'Killed' if pit_row.iloc[5] in ['KILLED', 'TIMED_OUT', 'MEMORY_ERROR', 'RUN_ERROR'] else 'Survived'
            match_status = "match"
        else:
            # No exact match found; search for a row with the same class_name, mutator_type, and method name
            potential_matches = pit_df_clean[
                (pit_df_clean.iloc[:, 1] == class_name) &  # 2nd column for class_name
                (pit_df_clean.iloc[:, 2] == mutator_type) &  # 3rd column for mutator_type
                (pit_df_clean.iloc[:, 3].apply(lambda method_name: f" {method_name}(" in original_method.splitlines()[0] or f" {method_name} (" in original_method.splitlines()[0])) # 4th column for method name
                ]

            if not potential_matches.empty:
                pit_row = potential_matches.sample(1).iloc[0]
                pit_killed = 'Killed' if pit_row.iloc[5] in ['KILLED', 'TIMED_OUT', 'MEMORY_ERROR', 'RUN_ERROR'] else 'Survived'
                match_status = "no exact match"
            else:
                # If no match found based on class, mutator, and method
                pit_row = None
                pit_killed = 'None'
                match_status = "no match"

        if pit_row is not None:
            # Append the result to the matched_results list
            matched_results.append({
                'mutator_type': mutator_type,
                'original_method': llm_row['original_method'],
                'mutated_method': llm_row['mutated_method'],
                'compilable': llm_row['compilable'],
                'line_number': pit_row.iloc[4],
                'llm_killed': llm_killed,
                'pit_killed': pit_killed,
                'match_status': match_status
            })
        else:
            # No match found and no random match possible
            matched_results.append({
                'mutator_type': mutator_type,
                'original_method': llm_row['original_method'],
                'mutated_method': llm_row['mutated_method'],
                'compilable': llm_row['compilable'],
                'line_number': 'None',
                'llm_killed': llm_killed,
                'pit_killed': 'None',
                'match_status': "no match"
            })

    # Convert the matched results to a DataFrame
    results_df = pd.DataFrame(matched_results)

    # Write the results to the output CSV file
    results_df.to_csv(output_csv, index=False)

# Example usage:
llm_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/combined_mutation_results_with_line.csv'
pit_csv = '/Users/matt/Downloads/commons-imaging-1.0.0-alpha5-src/target/pit-reports/mutations.csv'
output_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/matched_mutation_results.csv'

compare_mutations(llm_csv, pit_csv, output_csv)