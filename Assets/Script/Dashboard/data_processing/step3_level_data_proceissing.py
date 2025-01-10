import json
from datetime import datetime

def parse_timestamp(timestamp):

    try:
        if timestamp.endswith("ZZ"):
            timestamp = timestamp[:-1]  
        
        cleaned_timestamp = timestamp[:-2] + "Z"  
        
        
        return datetime.strptime(cleaned_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        print(f"Failed to parse timestamp: {timestamp}, error: {e}")
        raise


def calculate_total_time(launched_timestamp, completed_timestamp):
    """
    Calculate the total time between launched and completed timestamps.

    Args:
        launched_timestamp (str): Launched timestamp.
        completed_timestamp (str): Completed timestamp.

    Returns:
        int: Total time in seconds, or -1 if completed_timestamp is missing.
    """
    if not completed_timestamp:
        return -1

    launched = parse_timestamp(launched_timestamp)
    completed = parse_timestamp(completed_timestamp)

    if launched and completed:
        return int((completed - launched).total_seconds())
    return -1

def count_keywords(executed_content):
    """
    Count occurrences of specific keywords in the executed content.

    Args:
        executed_content (list): List of executed content strings.

    Returns:
        dict: Dictionary with counts of keywords.
    """
    keywords = ["repeat", "turnleft", "turnright", "forward", "while", "not", "if", "else", "fieldgate", "wallfront", "or", "and", "wait", "exit", "turnback", "activate", ]
    counts = {keyword: 0 for keyword in keywords}

    for content in executed_content:
        for keyword in keywords:
            counts[keyword] += content.count(keyword)

    return counts

def process_level_data(input_file, output_file):
    """
    Process the level data JSON file and add total_time and keyword counts.

    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to save the processed JSON file.
    """
    with open(input_file, "r") as f:
        data = json.load(f)

    for user_id, levels in data.items():
        for level, games in levels.items():
            for game in games:
                # Calculate total time
                game["total_time"] = calculate_total_time(
                    game.get("launched_timestamp"),
                    game.get("completed_timestamp")
                )

                # Count keywords
                game["keyword_counts"] = count_keywords(game.get("executed_content", []))

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

# Example usage
if __name__ == "__main__":
    input_file = "spy_analysis/data/level_data.json"
    output_file = "spy_analysis/data/level_data_cleaned.json"
    process_level_data(input_file, output_file)
    print(f"Processing complete. Cleaned data saved to {output_file}.")
