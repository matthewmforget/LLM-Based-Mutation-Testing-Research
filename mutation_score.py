import pandas as pd
import re

def calculate_metrics(input_csv, output_csv):
    # Load the CSV file
    df = pd.read_csv(input_csv)

    # Group by the 'mutator_type' (mutation operator)
    grouped = df.groupby('mutator_type')

    # Initialize a list to store the metrics for each mutation operator
    metrics = []

    # Iterate over each group (mutation operator)
    for mutator_type, group in grouped:
        # Calculate the PIT mutation score
        pit_killed = group.apply(lambda row: row['pit_killed'] == 'Killed' or (row['match_status'] == 'no match' and row['llm_killed'] == 'Killed'), axis=1).sum()
        total_pit = len(group)
        pit_mutation_score = (pit_killed / total_pit) * 100 if total_pit > 0 else 0

        # Calculate the LLM mutation score
        llm_killed = group['llm_killed'].value_counts().get('Killed', 0)
        total_llm = len(group)
        llm_mutation_score = (llm_killed / total_llm) * 100 if total_llm > 0 else 0

        # Calculate the match percentage
        matches = group['match_status'].value_counts().get('match', 0)
        match_percentage = (matches / total_llm) * 100 if total_llm > 0 else 0

        # Calculate the compilable rate
        compilable_count = group['compilable'].value_counts().get(True, 0)  # Check for `True`
        compile_percentage = (compilable_count / total_llm) * 100 if total_llm > 0 else 0

        # Append the calculated metrics to the list
        metrics.append({
            'mutation': mutator_type,
            'PIT_mutation_score': f"{pit_mutation_score:.2f}%",
            'LLM_mutation_score': f"{llm_mutation_score:.2f}%",
            'matches': f"{match_percentage:.2f}%",
            'compile_percentage': f"{compile_percentage:.2f}%"
        })

    # Convert the metrics list to a DataFrame
    metrics_df = pd.DataFrame(metrics)

    # Write the results to the output CSV file
    metrics_df.to_csv(output_csv, index=False)

# Example usage:
input_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/matched_mutation_results.csv'
output_csv = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/LLM_mutation_results/imaging/mutation_operator_metrics.csv'

calculate_metrics(input_csv, output_csv)