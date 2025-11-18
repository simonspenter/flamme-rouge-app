# routes/scoreboard.py
from flask import Blueprint, render_template, request, redirect, jsonify
from services.db import get_db_connection
from constants.icons import stage_type_icons
from logic.scoring import calculate_points

scoreboard_bp = Blueprint("scoreboard_bp", __name__)

@scoreboard_bp.route("/scoreboard")
def scoreboard():
    race_id = request.args.get('race')
    if not race_id:
        return redirect('/scoreboard_input')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT code, teams, assistant FROM races WHERE id = ?", (race_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Race not found"}), 404

    code, teams, assistant = row

    cursor.execute("SELECT team_name FROM teams WHERE race_id = ?", (race_id,))
    team_names = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT team_id, rider_id, rider_name FROM riders WHERE race_id = ?", (race_id,))
    rider_names, rider_ids = {}, {}
    for team_id, rider_id, rider_name in cursor.fetchall():
        rider_names.setdefault(team_id, []).append(rider_name)
        rider_ids.setdefault(team_id, []).append(rider_id)

    total_classement_data = {tid: {rid: 0 for rid in rider_ids.get(tid, [])} for tid in rider_ids}

    cursor.execute("""
        SELECT id, number, name, start_location, end_location, type,
               length_km, elevation_m, route, route_image, link
        FROM stages WHERE race_code = ? ORDER BY number
    """, (code,))
    stage_data = []
    for stage in cursor.fetchall():
        stage_dict = {
            "id": stage[0], "number": stage[1], "name": stage[2],
            "start": stage[3], "end": stage[4], "type": stage[5],
            "length_km": stage[6], "elevation_m": stage[7],
            "route": stage[8], "route_image": stage[9], "link": stage[10],
            "segments": []
        }
        cursor.execute("""
            SELECT id, name, type, category, order_in_stage
            FROM segments WHERE stage_id = ? ORDER BY order_in_stage
        """, (stage[0],))
        for segment_id, name, seg_type, cat, order in cursor.fetchall():
            stage_dict["segments"].append({
                "id": segment_id, "name": name, "type": seg_type,
                "category": cat, "order": order
            })
        stage_data.append(stage_dict)

    # --- Load stage winners (keyed by stage number) ---
    cursor.execute("""
        SELECT s.number AS stage_number, w.rider_id
        FROM stage_winner w
        JOIN stages s ON w.stage_id = s.id
        WHERE w.race_id = ?
    """, (race_id,))

    stage_winner_map = {row[0]: row[1] for row in cursor.fetchall()}


    conn.close()

    return render_template(
        "scoreboard.html",
        race_id=race_id,
        stages=len(stage_data),
        teams=teams,
        team_names=team_names,
        rider_names=rider_names,
        rider_ids=rider_ids,
        stage_data=stage_data,
        total_classement_data=total_classement_data,
        stage_type_icons=stage_type_icons,
        assistant=3 if assistant == 3 else 2,
        enumerate=enumerate,
        stage_winner_map=stage_winner_map
    )

@scoreboard_bp.route('/scoreboard_input', methods=['GET', 'POST'])
def scoreboard_input():
    return render_template('scoreboard_input.html')

@scoreboard_bp.route('/api/verify_race')
def verify_race():
    race_id = request.args.get('race')
    if not race_id:
        return jsonify({"error": "Race ID is missing"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM races WHERE id = ?", (race_id,))
    ok = cursor.fetchone()
    conn.close()
    return jsonify({"status": "success"}) if ok else (jsonify({"error": "Race not found"}), 404)

@scoreboard_bp.route('/update-classement-result', methods=['POST'])
def update_classement_result():
    data = request.get_json()
    race_id = data.get('race_id')
    stage_number = data.get('stage_number')
    team_id = data.get('team_id')
    rider_id = data.get('rider_id')
    placement = data.get('placement')
    if not all([race_id, stage_number, team_id, rider_id, placement is not None]):
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM classement_results
        WHERE race_id = ? AND stage_id = ? AND team_id = ? AND rider_id = ?
    """, (race_id, stage_number, team_id, rider_id))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE classement_results SET placement = ? WHERE id = ?",
                       (placement, row[0]))
    else:
        cursor.execute("""
            INSERT INTO classement_results (race_id, stage_id, rider_id, team_id, placement)
            VALUES (?, ?, ?, ?, ?)
        """, (race_id, stage_number, rider_id, team_id, placement))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@scoreboard_bp.route("/api/classement_data")
def get_classement_data():
    race_id = request.args.get('race')
    if not race_id:
        return jsonify({"error": "race_id is missing"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stage_id, team_id, rider_id, placement
        FROM classement_results WHERE race_id = ?
    """, (race_id,))
    classement_data = cursor.fetchall()
    classement_dict, total_classement_data = {}, {}
    for stage_id, team_id, rider_id, placement in classement_data:
        classement_dict.setdefault(stage_id, {}).setdefault(team_id, {})[rider_id] = int(placement) if placement else 0
        total_classement_data.setdefault(team_id, {})[rider_id] = total_classement_data.setdefault(team_id, {}).get(rider_id, 0) + (int(placement) if placement else 0)
    # Normalize by global minimum
    all_scores = [v for team in total_classement_data.values() for v in team.values()]
    if all_scores:
        min_score = min(all_scores)
        for t in total_classement_data:
            for r in total_classement_data[t]:
                total_classement_data[t][r] -= min_score
    conn.close()
    return jsonify({"classement_data": classement_dict, "total_classement_data": total_classement_data})

@scoreboard_bp.route('/update-segment-result', methods=['POST'])
def update_segment_result():
    data = request.get_json()
    race_id = data.get('race_id')
    stage_number = data.get('stage_number')
    segment_id = data.get('segment_id')
    team_id = data.get('team_id')
    rider_id = data.get('rider_id')
    segment_category = data.get('segment_category')
    segment_type = data.get('segment_type')
    placement = data.get('placement')
    points = calculate_points(segment_category, placement)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM segment_results
        WHERE race_id = ? AND stage_id = ? AND segment_id = ? AND team_id = ? AND rider_id = ?
    """, (race_id, stage_number, segment_id, team_id, rider_id))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM segment_results WHERE id = ?", (row[0],))
    cursor.execute("""
        INSERT INTO segment_results (race_id, segment_id, rider_id, team_id, placement, points, segment_type, stage_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (race_id, segment_id, rider_id, team_id, placement, points, segment_type, stage_number))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@scoreboard_bp.route("/api/segment_data")
def get_segment_data():
    race_id = request.args.get('race')
    segment_type = request.args.get('segment_type')
    if not race_id or not segment_type:
        return jsonify({"error": "race_id or segment_type is missing"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT stage_id, team_id, rider_id, points, segment_type
        FROM segment_results WHERE race_id = ? AND segment_type = ?
    """, (race_id, segment_type))
    rows = cursor.fetchall()
    segment_dict, total_segment_data = {}, {}
    for stage_id, team_id, rider_id, points, _ in rows:
        segment_dict.setdefault(stage_id, {}).setdefault(team_id, {})
        segment_dict[stage_id][team_id][rider_id] = segment_dict[stage_id][team_id].get(rider_id, 0) + points
        total_segment_data.setdefault(team_id, {})
        total_segment_data[team_id][rider_id] = total_segment_data[team_id].get(rider_id, 0) + points
    conn.close()
    return jsonify({"segment_data": segment_dict, "total_segment_data": total_segment_data})

@scoreboard_bp.route('/update-stage-winner', methods=['POST'])
def update_stage_winner():
    data = request.get_json()

    race_id = data.get('race_id')
    stage_id = data.get('stage_id')
    rider_id = data.get('rider_id')
    team_id = data.get('team_id')

    if not all([race_id, stage_id, rider_id, team_id]):
        return jsonify({"status": "error", "message": "Missing data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Remove any existing winner for this stage
    cursor.execute("""
        DELETE FROM stage_winner
        WHERE race_id = ? AND stage_id = ?
    """, (race_id, stage_id))

    # Insert the new winner
    cursor.execute("""
        INSERT INTO stage_winner (race_id, stage_id, rider_id, team_id)
        VALUES (?, ?, ?, ?)
    """, (race_id, stage_id, rider_id, team_id))

    conn.commit()
    conn.close()

    return jsonify({"status": "success"})
