from flask import Flask, render_template, request, redirect, url_for
import os

# Race mapping
from races.stages import races_info
from races.race_info import sprint_categories, mountain_categories

# Database related
import pyodbc
import uuid
from datetime import datetime

# Load Database URL on flask
#from dotenv import load_dotenv
#load_dotenv()


app = Flask(__name__) 


# Get database connection string from environment
DATABASE_URL = DATABASE_URL = (
    os.environ.get('SQLCONNSTR_DATABASE_URL') or
    os.environ.get('ConnectionStrings:DATABASE_URL') or
    os.environ.get('DATABASE_URL')
)

def get_db_connection():
    """Create and return a database connection"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    return pyodbc.connect(DATABASE_URL)

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

@app.route("/create-race", methods=["POST"])
def create_race_submit():
    code = request.form.get("race")          # e.g. 'tdf2023'
    teams = int(request.form.get("teams"))
    assistant = request.form.get("assistant") == "on"

    if code not in races_info:
        return "Invalid race template selected.", 400

    race_id = create_race_in_db(code, teams, assistant)
    return redirect(url_for("scoreboard", race=race_id))


def create_race_in_db(code, teams, assistant):
    conn = get_db_connection()
    cursor = conn.cursor()

    race_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Insert the race
    cursor.execute("""
        INSERT INTO races (id, code, teams, assistant, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (race_id, code, teams, assistant, now))

    stage_data = races_info[code]

    for stage_num, stage_dict in stage_data.items():
        cursor.execute("""
            INSERT INTO stages (
                race_id, number, name, start_location, end_location, type,
                length_km, elevation_m, route, route_image, link
            )
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            race_id,
            stage_num,
            stage_dict.get("name"),
            stage_dict.get("start"),
            stage_dict.get("end"),
            stage_dict.get("type"),
            stage_dict.get("length_km"),
            stage_dict.get("elevation_m"),
            stage_dict.get("route"),
            stage_dict.get("route_image"),
            stage_dict.get("link")
        ))

        stage_id = cursor.fetchone()[0]

        # Insert mountain segments
        for i, (name, cat) in enumerate(stage_dict.get("mountains", {}).items(), 1):
            cursor.execute("""
                INSERT INTO segments (stage_id, name, type, category, order_in_stage)
                VALUES (?, ?, 'mountain', ?, ?)
            """, (stage_id, name, cat, i))

        # Insert sprint segments
        for i, (name, cat) in enumerate(stage_dict.get("sprints", {}).items(), 1):
            cursor.execute("""
                INSERT INTO segments (stage_id, name, type, category, order_in_stage)
                VALUES (?, ?, 'sprint', ?, ?)
            """, (stage_id, name, cat, i))

    conn.commit()
    conn.close()
    return race_id

@app.route("/scoreboard")
def scoreboard():
    race_id = request.args.get('race')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch race info
    cursor.execute("SELECT code, teams, assistant FROM races WHERE id = ?", race_id)
    race_row = cursor.fetchone()

    if not race_row:
        return "Race not found.", 404

    code, teams, assistant = race_row

    # Fetch all stages for the race
    cursor.execute("""
        SELECT id, number, name, start_location, end_location, type,
               length_km, elevation_m, route, route_image, link
        FROM stages
        WHERE race_id = ?
        ORDER BY number
    """, race_id)

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
            "sprints": [],
            "mountains": []
        }

        # Fetch segments for this stage
        cursor.execute("""
            SELECT name, type, category, order_in_stage
            FROM segments
            WHERE stage_id = ?
            ORDER BY type, order_in_stage
        """, stage[0])

        for name, seg_type, cat, _ in cursor.fetchall():
            if seg_type == "mountain":
                stage_dict["mountains"].append((name, cat))
            else:
                stage_dict["sprints"].append((name, cat))

        stage_data.append(stage_dict)

    conn.close()

    return render_template(
        'scoreboard.html',
        stages=len(stage_data),
        teams=teams,
        assistant=3 if assistant else 2,
        stage_data=stage_data,
        mountain_categories=mountain_categories,
        sprint_categories=sprint_categories,
        stage_type_icons=stage_type_icons
    )

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