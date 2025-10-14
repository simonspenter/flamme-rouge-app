# routes/main.py
from flask import Blueprint, render_template

main_bp = Blueprint("main_bp", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/rules", methods=["GET", "POST"])
def rules():
    return render_template("rules.html")
