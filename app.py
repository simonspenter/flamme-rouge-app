# app.py
from flask import Flask
import os

# Blueprints
from routes.main import main_bp
from routes.race import race_bp
from routes.scoreboard import scoreboard_bp

def create_app():
    app = Flask(__name__)

    # (Optional) debug print of env — keep if useful
    print("DEBUG ENV VARS:")
    for k, v in os.environ.items():
        if "DATABASE" in k or "SQL" in k:
            print(f"{k} = {v}")

    # Register blueprints (no URL changes)
    app.register_blueprint(main_bp)
    app.register_blueprint(race_bp)
    app.register_blueprint(scoreboard_bp)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
