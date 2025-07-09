from flask import Flask, render_template, request, redirect, url_for, jsonify
import os

# Race mapping
from races.stages import races_info
from races.race_info import sprint_categories, mountain_categories

# Database related
import pyodbc
from datetime import datetime
import time 

# Generating race_ids
import random
import string

#Debugging
import logging

# Always load .env in local dev
#from dotenv import load_dotenv
#load_dotenv()

# Debug print to confirm loading
print("DEBUG ENV VARS:")
for k, v in os.environ.items():
    if "DATABASE" in k or "SQL" in k:
        print(f"{k} = {v}")



app = Flask(__name__) 

print("DEBUG ENV VARS:")
for k, v in os.environ.items():
    if "DATABASE" in k or "SQL" in k:
        print(f"{k} = {v}")

# Get database connection string from environment
DATABASE_URL = (
    os.environ.get('SQLCONNSTR_SQLCONNSTR_DATABASE_URL') or
    os.environ.get('SQLCONNSTR_DATABASE_URL') or
    os.environ.get('ConnectionStrings:DATABASE_URL') or
    os.environ.get('DATABASE_URL')
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

print("USING DATABASE_URL:", DATABASE_URL)

def get_db_connection(retries=3, delay=5):
    """
    Create and return a database connection with retry logic.
    Will attempt to connect up to `retries` times with `delay` seconds in between.
    """
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")

    for attempt in range(1, retries + 1):
        try:
            print(f"Connecting with: {DATABASE_URL} (attempt {attempt})")
            return pyodbc.connect(DATABASE_URL)
        except pyodbc.Error as e:
            print(f"Database connection failed (attempt {attempt} of {retries}): {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retry attempts failed.")
                raise



# Mapping for stage type icons
stage_type_icons = {
    "Cobble stone": "cobblestone.svg",
    "Flat": "flat.svg",
    "Hilly": "hilly.svg",
    "Mountain": "mountain.svg",
    "Time trial": "timetrial.svg",
}

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/create-race", methods=["GET"])
def create_race():
    return render_template("create_race.html")

def generate_short_race_id(length=6):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def generate_unique_race_id(cursor, length=6):
    while True:
        race_id = generate_short_race_id(length)
        cursor.execute("SELECT 1 FROM races WHERE id = ?", (race_id,))
        if not cursor.fetchone():
            return race_id


@app.route("/create-race", methods=["POST"])
def create_race_submit():
    code = request.form.get("race")          # e.g. 'tdf2023'
    teams = int(request.form.get("teams"))
    assistant = int(request.form.get("assistant"))
    
    # Debug: Check what data has been received
    print(f"Received race: {code}, teams: {teams}, assistant: {assistant}")
    
    # Retrieve team names from the form
    team_names = [request.form.get(f"team_name_{i}") for i in range(1, teams + 1)]
    print(f"Team names: {team_names}")

    if code not in races_info:
        return "Invalid race template selected.", 400

    race_id = create_race_in_db(code, teams, assistant, team_names)

    # Debug: Check the race_id after creation
    print(f"Created race with ID: {race_id}")

    return redirect(url_for("scoreboard", race=race_id))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_race_in_db(code, teams, assistant, team_names):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Debug: Print the received parameters
    print(f"Creating race with code: {code}, teams: {teams}, assistant: {assistant}, team_names: {team_names}")

    # Generate a unique race ID
    race_id = generate_unique_race_id(cursor)
    now = datetime.utcnow()

    # Debug: Confirm the race_id generated
    print(f"Generated race_id: {race_id}")

    # Insert the race into the races table
    cursor.execute("""INSERT INTO races (id, code, teams, assistant, created_at) 
                      VALUES (?, ?, ?, ?, ?)""",
                   (race_id, code, teams, assistant, now))

    conn.commit()

    # Ensure the number of team names matches the number of teams selected
    if len(team_names) != teams:
        print("ERROR: Number of team names does not match the number of teams!")
        return None

    # Insert teams for the created race
    for team_number in range(teams):
        team_name = team_names[team_number].strip()  # Get team name, stripping any extra spaces
        team_id = create_team_in_db(race_id, team_number + 1, team_name)
        print(f"Inserted team {team_number + 1} with name {team_name} and ID {team_id}")

        # Insert riders for each team (example: 6 riders per team)
        for rider_number in range(1, 7):  # You can adjust this number as needed
            rider_name = f"Rider {team_number + 1}-{rider_number}"
            rider_id = create_rider_in_db(race_id, team_id, rider_number, rider_name)
            print(f"Inserted rider {rider_number} for team {team_number + 1} with ID {rider_id}")

    conn.close()

    # Debug: Confirm race and data insertion
    print(f"Race with ID: {race_id} inserted into the database with {teams} teams and riders.")

    return race_id


def create_team_in_db(race_id, team_number, team_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Debug: Print details about the team being created
    print(f"Creating team {team_number} for race {race_id} with name {team_name}")

    cursor.execute("""INSERT INTO teams (race_id, team_number, team_name) 
                      VALUES (?, ?, ?)""", (race_id, team_number, team_name))

    conn.commit()

    # Retrieve the team ID after insertion
    cursor.execute("SELECT team_id FROM teams WHERE race_id = ? AND team_number = ?", (race_id, team_number))
    team_id = cursor.fetchone()[0]
    print(f"Created team with ID: {team_id}")

    conn.close()

    return team_id


def create_rider_in_db(race_id, team_id, rider_number, rider_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Debugging output
    print(f"DEBUG: race_id={race_id}, team_id={team_id}, rider_name={rider_name}, rider_number={rider_number}")
    
    try:
        cursor.execute("""INSERT INTO riders (race_id, team_id, rider_name, rider_number) 
                          VALUES (?, ?, ?, ?)""", 
                       (race_id, team_id, rider_name, rider_number))
        conn.commit()
        print("DEBUG: Rider inserted successfully")  # Confirmation message
    except Exception as e:
        print(f"ERROR: {e}")  # Print out any errors that occur

    conn.close()




@app.route("/scoreboard")
def scoreboard():
    race_id = request.args.get('race')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch race info
    cursor.execute("SELECT code, teams, assistant FROM races WHERE id = ?", (race_id,))

    race_row = cursor.fetchone()

    if not race_row:
        return "Race not found.", 404

    code, teams, assistant = race_row

    # Fetch all stages for the race
    cursor.execute("""
        SELECT id, number, name, start_location, end_location, type,
            length_km, elevation_m, route, route_image, link
        FROM stages
        WHERE race_code = ?
        ORDER BY number
    """, (code,))


    stage_data = []
    for stage in cursor.fetchall():
        stage_dict = {
            "id": stage[0],
            "number": stage[1],
            "name": stage[2],
            "start": stage[3],
            "end": stage[4],
            "type": stage[5],
            "length_km": stage[6],
            "elevation_m": stage[7],
            "route": stage[8],
            "route_image": stage[9],
            "link": stage[10],
            "segments": []  # Create a unified segments list
        }

        # Fetch segments for this stage
        cursor.execute("""
            SELECT name, type, category, order_in_stage
            FROM segments
            WHERE stage_id = ?
            ORDER BY order_in_stage
        """, stage[0])

        for name, seg_type, cat, order in cursor.fetchall():
            stage_dict["segments"].append({
                "name": name,
                "type": seg_type,
                "category": cat,
                "order": order
            })

        # Sort segments by the 'order' field
        stage_dict["segments"].sort(key=lambda x: x["order"])

        stage_data.append(stage_dict)

    conn.close()

    return render_template(
        'scoreboard.html',
        stages=len(stage_data),
        teams=teams,
        assistant = 3 if assistant == 3 else 2,
        stage_data=stage_data,
        mountain_categories=mountain_categories,
        sprint_categories=sprint_categories,
        stage_type_icons=stage_type_icons
    )

@app.route('/update-segment-result', methods=['POST'])
def update_segment_result():
    data = request.get_json()

    stage_number = data['stage_number']
    segment_index = data['segment_index']
    segment_type = data['type']  # 'sprint' or 'mountain'
    category = data['category']
    team = data['team']
    rider = data['rider']
    position = data['position']
    race_id = request.args.get("race")  # You might pass this another way if needed

    # Look up stage_id based on race_code and stage_number
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM stages
        WHERE race_code = (SELECT code FROM races WHERE id = ?) AND number = ?
    """, (race_id, stage_number))
    stage_row = cursor.fetchone()
    if not stage_row:
        conn.close()
        return jsonify({"error": "Stage not found"}), 404

    stage_id = stage_row[0]

    # Look up segment_id based on order, type, and stage_id
    cursor.execute("""
        SELECT id FROM segments
        WHERE stage_id = ? AND type = ? AND order_in_stage = ?
    """, (stage_id, segment_type, segment_index + 1))  # `segment_index + 1` to match the order
    segment_row = cursor.fetchone()
    if not segment_row:
        conn.close()
        return jsonify({"error": "Segment not found"}), 404

    segment_id = segment_row[0]

    # Insert or update result
    cursor.execute("""
        MERGE segment_results AS target
        USING (SELECT ? AS segment_id, ? AS team, ? AS rider) AS source
        ON target.segment_id = source.segment_id AND target.team = source.team AND target.rider = source.rider
        WHEN MATCHED THEN
            UPDATE SET position = ?
        WHEN NOT MATCHED THEN
            INSERT (segment_id, team, rider, position) VALUES (?, ?, ?, ?);
    """, (segment_id, team, rider, position, position, segment_id, team, rider, position))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"}), 200



# Test route to verify database connection
@app.route("/test-db")
def test_db():
    try:
        if not DATABASE_URL:
            return "DATABASE_URL environment variable is not set"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        conn.close()
        return f"Database connected successfully! Test result: {result[0]}"
    except Exception as e:
        return f"Database connection failed: {str(e)}"

# Health check endpoint for Azure
@app.route("/health")
def health_check():
    """Health check endpoint for Azure monitoring"""
    return {"status": "healthy", "message": "Flask app is running"}, 200

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)