# routes/race.py
from flask import Blueprint, render_template, request, redirect, url_for
from services.db import get_db_connection
from logic.ids import generate_unique_race_id
from datetime import datetime

race_bp = Blueprint("race_bp", __name__)

@race_bp.route("/create-race", methods=["GET"])
def create_race():
    return render_template("create_race.html")

@race_bp.route("/create-race", methods=["POST"])
def create_race_submit():
    code = request.form.get("race")
    teams = int(request.form.get("teams"))
    assistant = int(request.form.get("assistant"))
    team_names = [request.form.get(f"team_name_{i}") for i in range(1, teams + 1)]
    rider_names = request.form  # you used this as a dict

    race_id = create_race_in_db(code, teams, assistant, team_names, rider_names)
    return redirect(url_for("scoreboard_bp.scoreboard", race=race_id))

def create_race_in_db(code, teams, assistant, team_names, rider_names):
    conn = get_db_connection()
    cursor = conn.cursor()

    race_id = generate_unique_race_id(cursor)
    now = datetime.utcnow()

    cursor.execute("""INSERT INTO races (id, code, teams, assistant, created_at)
                      VALUES (?, ?, ?, ?, ?)""", (race_id, code, teams, assistant, now))
    conn.commit()

    for team_number in range(1, teams + 1):
        if team_names and len(team_names) >= team_number:
            team_name = team_names[team_number - 1] or f"Team {team_number}"
        else:
            team_name = request.form.get(f"team_name_{team_number}") or f"Team {team_number}"

        team_id = create_team_in_db(race_id, team_number, team_name)

        num_riders = 3 if assistant == 3 else 2
        for rider_number in range(1, num_riders + 1):
            if rider_number == 1:
                rider_position = "Roleur"
            elif rider_number == 2:
                rider_position = "Sprinter"
            else:
                rider_position = "Assistant"

            key = f"rider_name_team{team_number}_rider{rider_number}"
            rider_name = rider_names.get(key) or f"{team_name} {rider_position}"
            create_rider_in_db(race_id, team_id, rider_number, rider_name, rider_position)

    conn.close()
    return race_id

def create_team_in_db(race_id, team_number, team_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO teams (race_id, team_number, team_name)
                      VALUES (?, ?, ?)""", (race_id, team_number, team_name))
    conn.commit()

    cursor.execute("SELECT team_id FROM teams WHERE race_id = ? AND team_number = ?",
                   (race_id, team_number))
    team_id = cursor.fetchone()[0]
    conn.close()
    return team_id

def create_rider_in_db(race_id, team_id, rider_number, rider_name, rider_position):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO riders (race_id, team_id, rider_name, rider_number, rider_position)
                      VALUES (?, ?, ?, ?, ?)""",
                   (race_id, team_id, rider_name, rider_number, rider_position))
    conn.commit()
    conn.close()
