from flask import Blueprint, render_template

comum = Blueprint("comum", __name__)

@comum.route("/")
def home():
    return render_template("index.html")
