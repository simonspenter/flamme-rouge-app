from flask import Flask, render_template, request, redirect, url_for
from races.stages import races_info
from races.race_info import sprint_categories, mountain_categories

app = Flask(__name__)

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
        sprint_categories=sprint_categories
    )

if __name__ == "__main__":
    app.run(debug=True)