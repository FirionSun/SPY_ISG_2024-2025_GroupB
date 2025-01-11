from step1_download_users_statements import process_user_statements
from step2_statements_raw_data_processing import process_statements_from_file
from step3_level_data_proceissing import process_level_data
from step4_level_data_general_processing import process_level_data_general_with_competencies
import sys
import os
import json

# Define the path to store the last used session IDs
LAST_SESSION_FILE = "Assets/Script/Dashboard/data/last_session_ids.json"

def save_last_session_ids(user_ids):
    """
    Save the provided session IDs to a file.
    """
    with open(LAST_SESSION_FILE, "w") as file:
        json.dump(user_ids, file)
    print(f"Saved session IDs to {LAST_SESSION_FILE}.")

def load_last_session_ids():
    """
    Load the last used session IDs from a file.
    If the file does not exist, return the default session IDs.
    """
    if os.path.exists(LAST_SESSION_FILE):
        with open(LAST_SESSION_FILE, "r") as file:
            return json.load(file)
    return ["3D37C851", "59B6B585", "4C6ED003", "6DFE62E7"]  # Default session IDs

def process_all_steps(user_ids=None):
    """
    Run all processing steps (1–4) for the specified user IDs.

    Args:
        user_ids (list): List of user session IDs to process. If None, use the last saved or default user list.
    """
    # Load last session IDs if none are provided
    if user_ids is None:
        print("No session IDs provided. Loading last used session IDs...")
        user_ids = load_last_session_ids()
        print(f"Loaded session IDs: {user_ids}")

    # Save the current session IDs for future reference
    save_last_session_ids(user_ids)

    # Step 1: Download user statements
    step1_output_file = "Assets/Script/Dashboard/data/step1_lrs_raw_user_statements.json"
    print(f"Starting Step 1: Downloading statements for users {user_ids}...")
    process_user_statements(user_ids, step1_output_file)
    print(f"Step 1 completed. Output saved to {step1_output_file}.\n")

    # Step 2: Process raw statements data
    step2_input_file = step1_output_file
    step2_output_file = "Assets/Script/Dashboard/data/step2_processed_user_statements.json"
    print(f"Starting Step 2: Processing raw statements from {step2_input_file}...")
    process_statements_from_file(step2_input_file, step2_output_file)
    print(f"Step 2 completed. Output saved to {step2_output_file}.\n")

    # Step 3: Clean and process level data
    step3_input_file = step2_output_file
    step3_output_file = "Assets/Script/Dashboard/data/step3_level_game_sessions.json"
    print(f"Starting Step 3: Cleaning and processing level data from {step3_input_file}...")
    process_level_data(step3_input_file, step3_output_file)
    print(f"Step 3 completed. Output saved to {step3_output_file}.\n")

    # Step 4: Generate general level information and match competencies
    step4_input_file = step3_output_file
    competency_file = "Assets/Script/Dashboard/data/competenciesReferential.json"
    step4_output_file = "Assets/Script/Dashboard/data/step4_level_summary_data.json"
    print(f"Starting Step 4: Generating general level data and matching competencies from {step4_input_file}...")
    process_level_data_general_with_competencies(step4_input_file, competency_file, step4_output_file)
    print(f"Step 4 completed. Final output saved to {step4_output_file}.\n")

    print("All processing steps completed successfully.")

if __name__ == "__main__":
    # Allow user to provide session IDs via command line, otherwise use last saved or default
    user_ids = None
    if len(sys.argv) > 1:
        user_ids = sys.argv[1:]
    
    process_all_steps(user_ids)
