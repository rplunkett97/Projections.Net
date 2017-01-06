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

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///stats.db")

@app.route("/")
@login_required
def index():

    #get a list of a users total players
    players = db.execute("SELECT * FROM projections WHERE owner = :user_id", user_id = session["user_id"])

    return render_template("index.html", players=players)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add player to team."""
    if request.method == "GET":
        return render_template("add.html")
        
    if request.method == "POST":
    
        #ensure that user has input player name
        player_name = request.form.get("player_name")
        if not player_name:
            return apology("input a player")
        exists = db.execute("SElECT * from projections WHERE Player = :player_name", player_name=player_name)
        if not exists:
            return apology("must input valid player name")
            
        #ensure that player is available
        owner = db.execute("SELECT owner FROM projections WHERE player = :name", name = player_name)
        if not owner:
            return apology("player already owned")

        #get info on user team
        #roster_number = db.execute("SELECT COUNT(*) FROM projections WHERE owner = :user", user=session["user_id"])
        #roster_number = int(roster_number)
        
        #ensure valid add
        #if roster_number >= 12:
         #   return apology("roster full")
        
        #otherwise, add player to team
        db.execute("UPDATE projections SET owner = :user WHERE player = :name", user = session["user_id"], name = player_name)

        # redirect user to home page
        return redirect(url_for("index"))
        

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")



        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("compare.html")
    
    if request.method == "POST":
        return apology("TODO")

    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    session.clear()
    
    #if user reached route via GET
    if request.method == "GET":
        return render_template("register.html")
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        
        #ensure username is not taken
        elif db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")):
                return apology("username already taken")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        # ensure passwords confirm
        elif request.form.get("password") != request.form.get("confirm password"):
            return apology("passwords don't match")

        #add user to database
        user = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=pwd_context.encrypt(request.form.get("password")) )

        #log user in
        session["user_id"] = user
        
        # redirect user to home page
        return redirect(url_for("index"))

@app.route("/drop", methods=["GET", "POST"])
@login_required
def drop():
    """Drop a player from your team"""
    if request.method == "GET":
        return render_template("drop.html")
    
    if request.method == "POST":
        
        #ensure valid player input
        name = request.form.get("player_name")
        if not name:
            return apology("must input player")
            
        player = db.execute("SELECT * FROM projections WHERE player = :name", name=name)
        if not player:
            return apology("must input valid player")
            
        if player[0]["owner"] != session["user_id"]:
            return apology("player not on team")
            
        #else, drop the player from the team
        db.execute("UPDATE projections SET owner = NULL WHERE player = :player", player = name)
        
        # redirect user to home page
        return redirect(url_for("index"))
        