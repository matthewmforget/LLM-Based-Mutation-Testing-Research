import subprocess
import os
import csv
import shutil
from LLM_Training_PIT import generate_mutants

# Global counters for mutations and project copies
mutation_counter = 1
copy_counter = 1

# Function to apply a mutation to the specified lines of code in a file
def apply_mutation(class_name, mutated_code, start_line, end_line, dst):
    # Convert the class name to a file path
    class_name = class_name.split('$')[0]
    file_path = os.path.join(dst, "src/main/java", class_name.replace('.', '/') + '.java')
    print(f"Mutating file: {file_path}")

    global mutation_counter  # Declare it as global to modify the global variable
    mutation_counter += 1

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Validate line numbers
        if start_line < 0 or end_line > len(lines) or start_line >= end_line:
            print("Invalid line numbers.")
            return None

        # Extract original method for debugging purposes
        original_method = ''.join(lines[start_line:end_line])
        print(f"Original Method:\n{original_method}")

        # Ensure proper formatting of mutated code
        mutated_code_lines = [line + '\n' for line in mutated_code.split('\n')]

        # Create new content with mutated method
        new_content = lines[:start_line] + mutated_code_lines + lines[end_line:]

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_content)

        print(f"Mutated file saved at {file_path}")
        return file_path
    except Exception as e:
        print(f"Error applying mutation: {e}")
        return None

# Function to copy the project and get the destination path
def copy_project(src, dst):
    try:
        # Copy the entire project
        shutil.copytree(src, dst)
        print(f"Project copied from {src} to {dst}")
        return dst
    except Exception as e:
        print(f"Error copying project: {e}")
        return None

# Function to run tests with Maven
def run_tests_with_maven(dst, timeout=2400):
    project_directory = dst

    # Compile the project
    compile_process = subprocess.run(
        ["mvn", "clean", "compile"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=project_directory
    )
    if compile_process.returncode != 0:
        print(f"Compilation failed:\n{compile_process.stderr.decode('utf-8')}")
        return False, True, False

    # Run the tests
    try:
        test_process = subprocess.run(
            ["mvn", "test"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_directory,
            timeout=timeout
    )

    except subprocess.TimeoutExpired:
        print(f"Tests timed out after {timeout} seconds.")
        return True, True, True  # Treat as a failure if the test times out

    if "BUILD FAILURE" in test_process.stdout.decode('utf-8'):
        print(f"Tests failed:\n{test_process.stdout.decode('utf-8')}")
        return True, True, False

    return True, False, False

# Main function to handle the mutation testing process
def main():
    global copy_counter
    src = "/Users/matt/Downloads/commons-imaging-1.0.0-alpha5-src"
    dst_base = "/Users/matt/Downloads/commons-imaging-1.0.0-alpha5-src"
    mutants, original_methods = generate_mutants()  # Call the function to get mutants

    results = []  # List to store the results for each mutant

    for (mutated_code, class_name, start_line, end_line), original_method in zip(mutants, original_methods):
        dst = f"{dst_base}-{copy_counter}"
        copy_counter += 1
        project_copy = copy_project(src, dst)

        if project_copy:
            mutated_file = apply_mutation(class_name, mutated_code, start_line, end_line, dst)
            if mutated_file:
                compilable, killed, timeout = run_tests_with_maven(dst)

                # Record the result
                results.append({
                    "class_name": class_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "original_method": original_method,
                    "mutated_method": mutated_code,
                    "compilable": compilable,
                    "mutation_score": 1 if killed else 0,
                    "timeout": timeout
                })
            else:
                # If the mutation couldn't be applied, it's not compilable
                results.append({
                    "class_name": class_name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "original_method": original_method,
                    "mutated_method": mutated_code,
                    "compilable": False,
                    "mutation_score": 0,
                    "timeout": timeout
                })

    # Calculate overall mutation score
    total_mutants = len(results)
    killed_mutants = sum(result["mutation_score"] for result in results)
    mutation_score = (killed_mutants / total_mutants) * 100 if total_mutants > 0 else 0
    print(f"Overall Mutation Score: {mutation_score:.2f}%")

    # Write results to CSV
    with open("mutation_results.csv", mode="w", newline='', encoding='utf-8') as csv_file:
        fieldnames = ["class_name", "start_line", "end_line", "original_method", "mutated_method",
                      "compilable", "mutation_score", "timeout"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print("Results written to mutation_results.csv")

if __name__ == "__main__":
    main()