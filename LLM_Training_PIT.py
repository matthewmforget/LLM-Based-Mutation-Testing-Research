import os
import pandas as pd
from openai import OpenAI
from collections import defaultdict

# Set your OpenAI API key
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define few-shot examples for the mutation task
few_shot_prompt = """
Below is an example of Java code and its mutated version using the BooleanFalseReturnValsMutator mutator, which replaces a boolean return value that is not already false with false. Here is an example:


Original:
public boolean isEven(int number) { 
    if (number > 2) {
        return false;
    }
    return number % 2 == 0; 
}


Mutated:
public boolean isEven(int number) { 
    if (number > 2) {
        return false;
    }
    return false; 
}
---
Notice how the mutator was only applied once.
Based on the above example, mutate the following java method, you must mutate one return value, but include only the entire mutated method in your response. Do not include any labels, annotations, other text, or formatting markers (e.g., ```java). Please only apply the mutation once in the following method:
"""

# Load the CSV file
csv_path = '/Users/matt/Documents/Fourth year/Mutation Testing/PIT-parsable/methods_with_lines.csv'  # Update this path
mutations_df = pd.read_csv(csv_path)

# Specify the mutator to filter
specified_mutator = 'org.pitest.mutationtest.engine.gregor.mutators.returns.BooleanFalseReturnValsMutator'  # Update this mutator to the one you want

# Filter the DataFrame to get methods for the specified mutator
filtered_df = mutations_df[mutations_df['mutator'] == specified_mutator]

## Initialize the required variables
unique_methods = []
selected_methods_info = []
class_counts = defaultdict(int)  # To track the number of times each class is selected

# Iterate through the DataFrame
for index, row in filtered_df.iterrows():
    if len(unique_methods) >= 10:
        break

    method = row['method_lines']
    class_name = row['class']
    start_line = row['start_line']
    end_line = row['end_line']

    # Check if the class has already been selected 4 times
    if class_counts[class_name] >= 4:
        continue  # Skip this row and move to the next one

    # If the method is not already in the list, consider it for selection
    if method not in unique_methods:
        unique_methods.append(method)
        selected_methods_info.append((method, class_name, start_line, end_line))
        class_counts[class_name] += 1  # Increment the count for this class

# List of methods to be mutated
methods_to_mutate = unique_methods

# Function to generate mutants
def generate_mutants():
    mutants = []
    for method, class_name, start_line, end_line in selected_methods_info:
        few_shot_prompt_final = few_shot_prompt + method

        # Generate mutants using the API
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a code assistant"},
                {"role": "user", "content": few_shot_prompt_final}
            ],
            model="gpt-3.5-turbo",
            temperature=0.0
        )

        # Extract the mutated code
        mutated_code = chat_completion.choices[0].message.content.strip()
        mutants.append((mutated_code, class_name, start_line, end_line))

        # Logging for verification
        print("Original Method:")
        print(method.strip())
        print("Mutated Code:")
        print(mutated_code)
        print(f"Class: {class_name}, Start Line: {start_line}, End Line: {end_line}")
        print("\n---\n")
        # print("Prompt tokens used:", chat_completion.usage['prompt_tokens'])
        # print("Completion tokens used:", chat_completion.usage['completion_tokens'])
        # print("Total tokens used:", chat_completion.usage['total_tokens'])

    return mutants, methods_to_mutate

# Generate and return mutants
if __name__ == "__main__":
    mutants = generate_mutants()