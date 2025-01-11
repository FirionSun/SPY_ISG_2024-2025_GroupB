import json
from xml.etree.ElementTree import Element, ElementTree

import re

def is_competency_match_with_level(competency, level_xml):
    """
    Check if a competency matches a given level.

    Args:
        competency (dict): The competency data, including filters and rule.
        level_xml (ElementTree): The level data in XML format.

    Returns:
        bool: True if the competency matches the level, False otherwise.
    """
    filters_state = {}

    for filter_data in competency["filters"]:
        label = filter_data["label"]
        tag = filter_data["tag"]

        if label in filters_state:
            if not filters_state[label]:  # No nodes identified, skip further checks
                continue
        else:
            # Initialize with all nodes of the specified tag
            filters_state[label] = list(level_xml.findall(f".//{tag}"))

        # Apply constraints on nodes
        tags = filters_state[label]
        for constraint in filter_data.get("constraints", []):
            attribute = constraint.get("attribute")
            constraint_type = constraint["constraint"]
            value = constraint.get("value")
            tag2 = constraint.get("tag2")
            attribute2 = constraint.get("attribute2")

            for t in range(len(tags) - 1, -1, -1):  # Iterate in reverse to allow removal
                node = tags[t]
                attr_value = node.attrib.get(attribute)

                if constraint_type == "=" and (attr_value is None or attr_value != value):
                    tags.pop(t)
                elif constraint_type == "<>" and (attr_value is None or attr_value == value):
                    tags.pop(t)
                elif constraint_type in [">", "<", ">=", "<="]:
                    try:
                        attr_value = int(attr_value) if attr_value else None
                        target_value = int(value)
                        if constraint_type == ">" and not (attr_value > target_value):
                            tags.pop(t)
                        elif constraint_type == "<" and not (attr_value < target_value):
                            tags.pop(t)
                        elif constraint_type == ">=" and not (attr_value >= target_value):
                            tags.pop(t)
                        elif constraint_type == "<=" and not (attr_value <= target_value):
                            tags.pop(t)
                    except ValueError:
                        tags.pop(t)
                elif constraint_type == "isIncludedIn" and (attr_value is None or value not in attr_value):
                    tags.pop(t)
                elif constraint_type == "sameValue":
                    related_nodes = level_xml.findall(f".//{tag2}")
                    if not any(node.attrib.get(attribute2) == attr_value for node in related_nodes if node is not tags[t]):
                        tags.pop(t)
                elif constraint_type == "hasChild" and not list(node):
                    tags.pop(t)

    # Evaluate the rule
    rule = competency["rule"]

    # Check if the rule is empty
    if not rule.strip():
        return False

    # Replace '=' with '==' to make it valid Python syntax
    rule = rule.replace("=", "==").replace("<==", "<=").replace(">==", ">=")

    # Replace filters with their respective counts
    for key, nodes in filters_state.items():
        rule = rule.replace(key, str(len(nodes)))

    # Replace undefined keys with 0 using regex
    undefined_keys = re.findall(r"\\b[a-zA-Z_]+\\b", rule)
    for key in undefined_keys:
        if key not in filters_state:
            rule = re.sub(rf"\\b{key}\\b", "0", rule)

    # Clean up extra spaces and ensure rule is valid
    rule = re.sub(r"\\s+", " ", rule).strip()

    if re.search(r"[a-zA-Z]+\\s[<>=]", rule):
        return False
    try:
        return eval(rule)
    except Exception as e:
        return False


import xml.etree.ElementTree as ET

def process_level_data_general_with_competencies(input_file, competency_file, output_file):
    """
    Process the level data to generate general information per level and evaluate competencies.

    Args:
        input_file (str): Path to the input JSON file.
        competency_file (str): Path to the competencies JSON file.
        output_file (str): Path to save the processed general JSON file.
    """
    with open(input_file, "r") as f:
        level_data = json.load(f)

    with open(competency_file, "r") as f:
        competencies_data = json.load(f)

    general_data = {}

    for user_id, levels in level_data.items():
        general_data[user_id] = {}

        for level, games in levels.items():
            # Parse the level XML (assuming XML file is available for each level)
            level_path = level.replace("levels/", "").replace("/", "/")  # Fix the path
            full_path = f"Assets/StreamingAssets/Levels/{level_path}"

            try:
                level_xml = ET.parse(full_path).getroot()
            except Exception as e:
                print(f"Failed to parse level XML for {level}: {e}")
                continue

            level_info = {
                "completed": False,
                "total_games": len(games),
                "total_games_completed": 0,
                "competence": [],
            }

            # Check if the level is completed (any game has a completed_timestamp)
            level_info["completed"] = any(game.get("completed_timestamp") for game in games)

            # Count the number of games with completed_timestamp
            level_info["total_games_completed"] = sum(1 for game in games if game.get("completed_timestamp"))

            # Evaluate competencies
            for competency in competencies_data["referentials"][0]["list"]:
                if is_competency_match_with_level(competency, level_xml):
                    level_info["competence"].append(competency["key"])

            general_data[user_id][level] = level_info

        # Save the processed data
    with open(output_file, "w") as f:
        json.dump(general_data, f, indent=4)


if __name__ == "__main__":
    input_file = "spy_analysis/data/level_data_cleaned.json"
    competency_file = "spy_analysis/data/competenciesReferential.json"
    output_file = "spy_analysis/data/level_data_general.json"

    process_level_data_general_with_competencies(input_file, competency_file, output_file)
    print(f"Processed general level data with competencies saved to {output_file}.")

