import os
from flask import Flask, jsonify, render_template, request
import pandas as pd
import json
from flask import request, jsonify
import subprocess


app = Flask(__name__)

# Get the absolute path of the current file (app.py) and return the path of its parent directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Set the path for the data folder
data_file_path = os.path.join(project_root, 'data', 'step3_level_game_sessions.json')
data_processing_path = os.path.join(project_root, 'data_processing', 'data_processing_all_in_one.py')
level_scores_file_path = os.path.join(project_root, 'data', 'scores_per_level.json')

@app.route("/refresh_data", methods=["POST"])
def refresh_data():
    # Debugging: Print the content type and request data
    print(f"Content-Type: {request.content_type}")
    print(f"Request data: {request.data}")

    # Check if content type is JSON
    if request.content_type != 'application/json':
        return jsonify({"message": "Unsupported Media Type. Expected application/json."}), 415
    
    # Handle cases where the body is empty
    try:
        session_ids = request.json.get("session_ids", []) if request.json else []
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return jsonify({"message": "Invalid JSON format."}), 400

    try:
        # Build the command for running the Python script
        command = ["python", data_processing_path]
        if session_ids:
            command.extend(session_ids)
        
        # Debugging: Print the command being executed
        print(f"Executing command: {command}")

        # Run the script
        subprocess.run(command, check=True)
        
        return jsonify({"message": "Data refreshed successfully!"}), 200
    except Exception as e:
        print(f"Error running script: {e}")
        return jsonify({"message": "Failed to refresh data."}), 500

# Load JSON file data
def load_data(path):
    """Load the JSON file from the specified path"""
    with open(path, 'r') as file:
        return json.load(file)
    
# Get three-star scores for each level
def get_three_stars_data():
    """Retrieve the three-star score data for each level"""
    level_scores = load_data(level_scores_file_path)  # Load level scores from file
    three_stars_data = {}

    for level, scores in level_scores.items():
        # Extract the three-star score for each level
        three_stars_data[level] = int(scores["threeStars"])

    return three_stars_data

def calculate_percentage_score(user_score, three_stars_score):
    """Calculate the percentage score"""
    if three_stars_score > 0:
        return (user_score / three_stars_score) * 100
    else:
        return 0  # Return 0 if the three-star score is 0 or invalid


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_users')
def get_users():
    # Load data from the data file
    data = load_data(data_file_path)

    # Get all user IDs
    users = list(data.keys())

    # Debugging output
    print("Loaded users:", users)

    return jsonify(users)


@app.route('/get_competence_data')
def get_competence_data():
    # Retrieve query parameter user_id
    user_id = request.args.get('user_id', 'all')

    # Load general level data file
    general_data_path = os.path.join(project_root, 'data', 'step4_level_summary_data.json')
    general_data = load_data(general_data_path)

    # Initialize counters
    competence_counts_user = {}  # Data for the current user
    competence_counts_all = {}  # Average data for the entire class

    # Aggregate data for the entire class
    user_competence_counts = {}
    for user, levels in general_data.items():
        user_competence_counts[user] = {}
        for level_info in levels.values():
            if level_info["completed"]:  # Only count completed levels
                for competence in level_info["competence"]:
                    user_competence_counts[user][competence] = (
                        user_competence_counts[user].get(competence, 0) + 1
                    )

    # Calculate the class average for each competence
    total_users = len(user_competence_counts)
    for user_counts in user_competence_counts.values():
        for competence, count in user_counts.items():
            if competence not in competence_counts_all:
                competence_counts_all[competence] = 0
            competence_counts_all[competence] += count

    competence_averages_all = {
        competence: total / total_users
        for competence, total in competence_counts_all.items()
    }

    # Aggregate data for the current user
    if user_id != 'all':
        user_data = general_data.get(user_id, {})
        for level_info in user_data.values():
            if level_info["completed"]:  # Only count completed levels
                for competence in level_info["competence"]:
                    competence_counts_user[competence] = competence_counts_user.get(competence, 0) + 1

    # Construct response data
    response_data = {
        "user_data": [
            {"competence": comp, "completed_levels": competence_counts_user.get(comp, 0)}
            for comp in sorted(competence_counts_user.keys(), key=lambda x: competence_counts_user.get(x, 0), reverse=True)
        ],
        "all_data": [
            {"competence": comp, "average_completed_levels": round(avg, 2)}
            for comp, avg in sorted(competence_averages_all.items(), key=lambda x: x[1], reverse=True)
        ]
    }

    return jsonify(response_data)


@app.route('/get_launch_completed_data')
def get_launch_completed_data():
    user_id = request.args.get('user_id', 'all')
    data = load_data(data_file_path)
    if user_id != 'all':
        data = {user_id: data.get(user_id, {})}

    records = []
    for user, levels in data.items():
        for level, sessions in levels.items():
            for session in sessions:
                records.append({
                    "user": user,
                    "level": level.replace("levels/", "").replace(".xml", ""),
                    "completed_timestamp": session.get("completed_timestamp")
                })

    df = pd.DataFrame(records)
    df['completed'] = df['completed_timestamp'].notna()
    df['launched'] = True

    level_counts = df.groupby('level').agg(
        launched=('launched', 'sum'),
        completed=('completed', 'sum')
    ).reset_index()

    return jsonify(level_counts.to_dict(orient='records'))


@app.route('/get_avg_time_data')
def get_avg_time_data():
    user_id = request.args.get('user_id', 'all')
    data = load_data(data_file_path)

    # Construct data records
    records = []
    for user, levels in data.items():
        for level, sessions in levels.items():
            for session in sessions:
                records.append({
                    "user": user,
                    "level": level.replace("levels/", "").replace(".xml", ""),
                    "total_time": session.get("total_time", -1)
                })

    df = pd.DataFrame(records)

    # Calculate class average
    avg_time_all = (
        df[df['total_time'] != -1]
        .groupby('level')['total_time']
        .mean()
        .reset_index()
        .rename(columns={'total_time': 'avg_time_all'})
    )

    # If a specific user is selected, calculate data for that user
    if user_id != 'all':
        user_data = df[(df['total_time'] != -1) & (df['user'] == user_id)]
        avg_time_user = (
            user_data.groupby('level')['total_time']
            .mean()
            .reset_index()
            .rename(columns={'total_time': 'avg_time_user'})
        )

        # Merge user data and class average data
        avg_time_combined = pd.merge(
            avg_time_user, avg_time_all, on='level', how='left'
        ).to_dict(orient='records')
    else:
        # Class data does not require user-specific data
        avg_time_combined = avg_time_all.to_dict(orient='records')

    return jsonify(avg_time_combined)


@app.route('/get_avg_score_data')
def get_avg_score_data():
    user_id = request.args.get('user_id', 'all')
    data = load_data(data_file_path)
    level_score_data = get_three_stars_data()

    records = []

    # Collect data for all users
    for user, levels in data.items():
        for level, sessions in levels.items():
            for session in sessions:
                user_score = session.get("score", 0)
                three_stars_score = level_score_data.get(level, 0)
                percentage_score = calculate_percentage_score(user_score, three_stars_score)
                records.append({
                    "user": user,
                    "level": level.replace("levels/", "").replace(".xml", ""),
                    "score": percentage_score
                })

    df = pd.DataFrame(records)

    # Class average scores
    completed_df_all = df[df['score'] > 0]
    avg_score_per_level_all = completed_df_all.groupby('level')['score'].mean().reset_index()
    avg_score_per_level_all = avg_score_per_level_all.rename(columns={'score': 'avg_score_all'})

    if user_id == 'all':
        # If class data is requested, only return class averages
        return jsonify(avg_score_per_level_all.to_dict(orient='records'))
    else:
        # Average scores for the current user
        df_user = df[df['user'] == user_id]
        completed_df_user = df_user[df_user['score'] > 0]
        avg_score_per_level_user = completed_df_user.groupby('level')['score'].mean().reset_index()
        avg_score_per_level_user = avg_score_per_level_user.rename(columns={'score': 'avg_score_user'})

        # Merge class and user data, retaining only levels with user scores
        avg_score_per_level = pd.merge(
            avg_score_per_level_user,
            avg_score_per_level_all,
            on='level',
            how='inner'  # Retain only levels with user scores
        )

        return jsonify(avg_score_per_level.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
