from datetime import datetime
import json
import os

def process_statements(user_statements):
    """
    Process statements for each user, grouping by levels and games.

    Args:
        user_statements (dict): Statements grouped by user and verb.

    Returns:
        dict: Processed structure with levels and game data.
    """
    processed_data = {}

    for user_id, verbs in user_statements.items():
        launched_statements = verbs.get("http://adlnet.gov/expapi/verbs/launched", [])
        completed_statements = verbs.get("http://adlnet.gov/expapi/verbs/completed", [])
        executed_statements = verbs.get("https://spy.lip6.fr/xapi/verbs/executed", [])

        # Sort launched statements by timestamp
        launched_statements.sort(key=lambda x: x["timestamp"])

        user_data = {}

        # Track launched statements that are matched to completed or executed
        matched_launched_ids = set()

        for completed in completed_statements:
            completed_timestamp = completed["timestamp"]
            completed_datetime = parse_timestamp(completed_timestamp)
            completed_actor = completed.get("actor", {}).get("account", {}).get("name")

            # Find the closest earlier launched statement
            closest_launched = None
            for launched in launched_statements:
                launched_actor = launched.get("actor", {}).get("account", {}).get("name")
                launched_timestamp = launched["timestamp"]
                launched_datetime = parse_timestamp(launched_timestamp)

                if launched_actor == completed_actor and launched_datetime <= completed_datetime:
                    closest_launched = launched
                else:
                    break

            if closest_launched:
                # Mark this launched as matched
                matched_launched_ids.add(closest_launched["id"])

                level = closest_launched.get("object", {}).get("definition", {}).get("extensions", {}).get("https://spy.lip6.fr/xapi/extensions/value")
                if level:
                    level = level[0]
                    game_data = {
                        "launched_timestamp": closest_launched["timestamp"],
                        "completed_timestamp": completed_timestamp,
                        "score": int(completed.get("result", {}).get("extensions", {}).get("https://spy.lip6.fr/xapi/extensions/score", [0])[0]),
                        "executed_content": []
                    }

                    # Group by level
                    if level not in user_data:
                        user_data[level] = []

                    user_data[level].append(game_data)

        # Process unmatched launched statements
        for launched in launched_statements:
            if launched["id"] not in matched_launched_ids:
                level = launched.get("object", {}).get("definition", {}).get("extensions", {}).get("https://spy.lip6.fr/xapi/extensions/value")
                if level:
                    level = level[0]
                    game_data = {
                        "launched_timestamp": launched["timestamp"],
                        "executed_content": []
                    }

                    if level not in user_data:
                        user_data[level] = []

                    user_data[level].append(game_data)

        # Add executed statements to the corresponding games
        for executed in executed_statements:
            executed_timestamp = executed["timestamp"]
            executed_datetime = parse_timestamp(executed_timestamp)
            executed_actor = executed.get("actor", {}).get("account", {}).get("name")
            executed_content = executed.get("object", {}).get("definition", {}).get("extensions", {}).get("https://spy.lip6.fr/xapi/extensions/content", [])

            # Find the closest earlier launched statement
            closest_launched = None
            for launched in launched_statements:
                launched_actor = launched.get("actor", {}).get("account", {}).get("name")
                launched_timestamp = launched["timestamp"]
                launched_datetime = parse_timestamp(launched_timestamp)

                if launched_actor == executed_actor and launched_datetime <= executed_datetime:
                    closest_launched = launched
                else:
                    break

            if closest_launched:
                level = closest_launched.get("object", {}).get("definition", {}).get("extensions", {}).get("https://spy.lip6.fr/xapi/extensions/value")
                if level:
                    level = level[0]
                    # Append executed content to the corresponding game
                    found = False
                    for game in user_data.get(level, []):
                        if game["launched_timestamp"] == closest_launched["timestamp"]:
                            game["executed_content"].extend(executed_content)
                            found = True
                            break
                    if not found:
                        print(f"No matching game found for executed statement: {executed}")
            else:
                print(f"No matching launched statement found for executed: {executed}")

        processed_data[user_id] = user_data

    return processed_data

def parse_timestamp(timestamp):
    """
    Parse a timestamp, handling various formats and ensuring it is properly cleaned.
    """
    try:
        if timestamp.endswith("ZZ"):
            timestamp = timestamp[:-1]
        cleaned_timestamp = timestamp[:-2] + "Z"
        return datetime.strptime(cleaned_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        print(f"Failed to parse timestamp: {timestamp}, error: {e}")
        raise

def save_processed_data(processed_data, filename="processed_statements.json"):
    """
    Save processed data to a JSON file.

    Args:
        processed_data (dict): Processed data.
        filename (str): File name to save the data.
    """
    with open(filename, "w") as f:
        json.dump(processed_data, f, indent=4)

def process_statements_from_file(input_file, output_file):
    """
    Process statements from an input JSON file and save to an output JSON file.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file.
    """
    with open(input_file, "r") as f:
        user_statements = json.load(f)

    processed_data = process_statements(user_statements)
    save_processed_data(processed_data, output_file)
    print(f"Processing complete. Processed data saved to {output_file}")

# Example Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python process_statements.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_statements_from_file(input_file, output_file)
