from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir

from helpers import *


# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///stats.db")

@app.route("/compare", methods=["GET", "POST"])
@login_required

# player_name = request.form.get("player_name")
compare_to = db.execute("SELECT VAFGpct, FTpct, ThreePM, TRB, AST, STL, BLK, PTS) FROM projections WHERE Player = :Player", Player='LeBron James')
compare_to_FGpct = compare_to[0][0]
compare_to_FTpct = compare_to[0][1]
compare_to_ThreePM = compare_to[0][2]
compare_to_TRB = compare_to[0][3]
compare_to_AST = compare_to[0][4]
compare_to_STL = compare_to[0][5]
compare_to_BLK = compare_to[0][6]
compare_to_PTS = compare_to[0][7]

print(compare_to_PTS)