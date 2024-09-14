import pandas as pd

# Load the CSV file
file_path = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/commons-net-3.11.1-src/target/pit-reports/mutations.csv'
mutations_df = pd.read_csv(file_path)

# Rename the columns for clarity
mutations_df.columns = [
    'File Name', 'Class Name', 'Mutator', 'Method',
    'Line Number', 'Status', 'Killing Test'
]

# Function to get the top 10 mutation operators
def get_top_mutation_operators(df, top_n=10):
    return df['Mutator'].value_counts().head(top_n)

# Function to get the classes and methods for the top mutators
def get_classes_and_methods_for_top_mutators(df, top_mutators):
    data = {
        'Top 10 Mutators': [],
        'Classes Applied To': [],
        'Methods Applied To': [],
        'Usage Count': [],  # New column for the number of times the mutator was used
        'Line Numbers': []  # New column for the line numbers
    }

    for mutator in top_mutators.index:
        applied_classes = df[df['Mutator'] == mutator]['Class Name'].unique()
        applied_methods = df[df['Mutator'] == mutator]['Method'].apply(lambda x: 'NaN' if pd.isna(x) else x).unique()
        usage_count = top_mutators[mutator]  # Get the count from the top_mutators Series
        line_numbers = df[df['Mutator'] == mutator]['Line Number'].apply(lambda x: str(x)).unique()  # Get the line numbers

        data['Top 10 Mutators'].append(mutator)
        data['Classes Applied To'].append(', '.join(applied_classes))
        data['Methods Applied To'].append(', '.join(applied_methods))
        data['Usage Count'].append(usage_count)  # Add the count to the new column
        data['Line Numbers'].append(', '.join(line_numbers))  # Add the line numbers to the new column

    return pd.DataFrame(data)

# Save the top 10 DataFrame to a new CSV file
def save_top_10_to_csv(df, output_file='top_10_mutations.csv'):
    top_mutators = get_top_mutation_operators(df)
    top_10_df = get_classes_and_methods_for_top_mutators(df, top_mutators)
    top_10_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    save_top_10_to_csv(mutations_df)
    print("Top 10 mutation operators, classes, and methods have been saved to 'top_10_mutations.csv'.")