from flask import Flask, render_template, request, redirect, url_for
import os
import pyodbc
from races.stages import races_info
from races.race_info import sprint_categories, mountain_categories

app = Flask(__name__)

# Get database connection string from environment
DATABASE_URL = os.environ.get('DATABASE_URL')

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

@app.route("/create-race")
def create_race():
    return render_template('create_race.html')

@app.route("/scoreboard")
def scoreboard():
    # Get data from the create_race.html form
    race_id = request.args.get('race')  # Now a string like 'tdf2023'
    teams = int(request.args.get('teams'))
    assistant = int(request.args.get('assistant'))

    # Get stage data from the races_info dictionary
    stage_data = races_info.get(race_id)

    if not stage_data:
        return "Invalid race selected.", 400

    return render_template(
        'scoreboard.html',
        stages=len(stage_data),
        teams=teams,
        assistant=assistant,
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