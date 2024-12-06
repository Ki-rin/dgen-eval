import os
import shutil
import pandas as pd
import yaml
from utils import yaml_to_excel, generate_guidelines, match_answers, evaluate_answers
from concurrent.futures import ThreadPoolExecutor

output_folders = ["../tests/"]

# Function to process a single section
def process_section(section_no, output_folders):
    try:
        # Stage 1: Create Excel file from YAML
        yaml_file = f"C:\\dgen-prompts\\dgen_prompts\\default\\odd\\section_{section_no}.yaml"
        with open(yaml_file, "r", encoding="utf-8") as yf:  # Use UTF-8 encoding
            yaml_data = yaml.safe_load(yf)

        excel_file = f"Section{section_no}_questions_and_guidelines.xlsx"
        yaml_to_excel(yaml_data, excel_file=excel_file)

        # Generate guidelines in parallel
        with ThreadPoolExecutor() as executor:
            executor.submit(generate_guidelines, excel_file)

        # Stage 2: Include answers and append with calculated metrics
        for output_folder in output_folders:
            q_file = excel_file
            eval_file = os.path.join(output_folder, f"Section{section_no}_eval.xlsx")
            shutil.copyfile(q_file, eval_file)

            markdown_file = os.path.join(output_folder, f"ODD_Section_{section_no}_short.md")

            # Run match_answers and evaluate_answers in parallel
            with ThreadPoolExecutor() as executor:
                executor.submit(read_markdown_and_process, markdown_file, eval_file)

    except Exception as e:
        print(f"Error processing Section {section_no}: {e}")

# Function to handle reading markdown files
def read_markdown_and_process(markdown_file, eval_file):
    try:
        with open(markdown_file, "r", encoding="utf-8") as md_file:  # Use UTF-8 encoding
            md_content = md_file.read()
        match_answers(md_content, eval_file)
        evaluate_answers(eval_file)
    except Exception as e:
        print(f"Error processing markdown file {markdown_file}: {e}")

# Function to merge evaluation files into a single Excel file
def merge_evaluation_files(output_folders, merged_output_file):
    merged_data = []

    for output_folder in output_folders:
        for section_no in range(1, 6):
            eval_file = os.path.join(output_folder, f"Section{section_no}_eval.xlsx")
            if os.path.exists(eval_file):
                try:
                    df = pd.read_excel(eval_file)
                    df.insert(0, "Section #", section_no)
                    df.insert(1, "Output Folder", output_folder)
                    merged_data.append(df)
                except Exception as e:
                    print(f"Error reading {eval_file}: {e}")

    if merged_data:
        try:
            merged_df = pd.concat(merged_data, ignore_index=True)
            merged_df.to_excel(merged_output_file, index=False)
            print(f"Merged data saved to {merged_output_file}")
        except Exception as e:
            print(f"Error saving merged file: {e}")
    else:
        print("No evaluation files found to merge.")

# Main execution
if __name__ == "__main__":
    with ThreadPoolExecutor() as executor:
        executor.map(process_section, range(1, 6), [output_folders] * 5)

    merged_output_file = "merged_eval_output.xlsx"
    merge_evaluation_files(output_folders, merged_output_file)
