from flask import jsonify, Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
from flask_jsglue import JSGlue

from helpers import *

class SQL(object):
    def __init__(self, url):
        try:
            self.engine = sqlalchemy.create_engine(url)
        except Exception as e:
            raise RuntimeError(e)
    def execute(self, text, *multiparams, **params):
        try:
            statement = sqlalchemy.text(text).bindparams(*multiparams, **params)
            result = self.engine.execute(str(statement.compile(compile_kwargs={"literal_binds": True})))
            # SELECT
            if result.returns_rows:
                rows = result.fetchall()
                return [dict(row) for row in rows]
            # INSERT
            elif result.lastrowid is not None:
                return result.lastrowid
            # DELETE, UPDATE
            else:
                return result.rowcount
        except sqlalchemy.exc.IntegrityError:
            return None
        except Exception as e:
            raise RuntimeError(e)
            
import os
import sqlalchemy

try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

import psycopg2

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(
 database=url.path[1:],
 user=url.username,
 password=url.password,
 host=url.hostname,
 port=url.port
)

# configure application
app = Flask(__name__)
JSGlue(app)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL(os.environ["DATABASE_URL"])

@app.route("/")
@login_required
def index():

    #get a list of a users total players and pass to index
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
            return render_template("add.html", error="*Input a player")
        exists = db.execute("SELECT * from projections WHERE \"Player\" = :player_name", player_name=player_name)
        if not exists:
            return render_template("add.html", error="*must input valid player name")
            
        #ensure that player is available
        owner = db.execute("SELECT owner FROM projections WHERE \"Player\" = :name", name = player_name)
        if not owner:
            return render_template("add.html", error="*player already owned")

        #otherwise, add player to team
        db.execute("UPDATE projections SET owner = :user WHERE \"Player\" = :name", user = session["user_id"], name = player_name)

        # redirect user to home page
        return redirect(url_for("index"))
        
@app.route("/find")
def find():
    """Search for players that match query."""
    """make a q variable and match using LIKE in SQL wth the wildcard at the beginning (for last names) and end (for first names) of the users input, searching projections(database) for matches"""
    q = "%%" + request.args.get("q") + "%%"
    rows = db.execute("SELECT * from projections where (\"Player\" LIKE :q)", q = q)
    
    """return matches as a json for autocomplete"""
    return jsonify(rows)
        
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Add player to team."""
    if request.method == "GET":
        return render_template("search.html")
        
    if request.method == "POST":
    
        #ensure that user has input player name
        player_name = request.form.get("player_name")
        if not player_name:
            return render_template("search.html", error="*input a player")
        players = db.execute("SELECT * from projections WHERE \"Player\" = :player_name", player_name=player_name)
        if not players:
            return render_template("search.html", error="*must input valid player name")

        # redirect user to home page
        return render_template("searched.html", players=players)       

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="*must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="*must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return render_template("login.html", error="*invalid username and/or password")



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
        #ensure that user has input player name
        player_name = request.form.get("player_name")
        if not player_name:
            return render_template("compare.html", error="*input a player")
        player = db.execute("SELECT * from projections WHERE \"Player\" = :player_name", player_name=player_name)
        if not player:
            return render_template("compare.html", error="*must input valid player name")
            
        #get a list of 10 nearest players, sorted by zscore rank
        player = db.execute("SELECT * FROM zscores where \"Player\" = :player_name", player_name=player_name)
        if not player:
            return render_template("compare.html", error="* no comparison available")
        rank = player[0]["rank"]
        matches = db.execute("SELECT * FROM zscores INNER JOIN projections ON zscores.\"Player\" = projections.\"Player\" WHERE ABS(:rank - rank) <= 10 ORDER BY rank", rank=rank)
        
        
        return render_template("compared.html", players = matches)

    

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
            return render_template("register.html", error="*must provide username")
        
        #ensure username is not taken
        elif db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username")):
                return render_template("register.html", error="*username already taken")

        # ensure password was submitted
        elif not request.form.get("password"):
            return render_template("register.html", error="*must provide password")
        
        # ensure passwords confirm
        elif request.form.get("password") != request.form.get("confirm password"):
            return render_template("register.html", error="*passwords don't match")

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
            return render_template("drop.html", error="*must input player")
            
        player = db.execute("SELECT * FROM projections WHERE \"Player\" = :name", name=name)
        if not player:
            return render_template("drop.html", error="*must input valid player")
            
        if player[0]["owner"] != session["user_id"]:
            return render_template("drop.html", error="*player not on team")
            
        #else, drop the player from the team
        db.execute("UPDATE projections SET owner = NULL WHERE \"Player\" = :player", player = name)
        
        # redirect user to home page
        return redirect(url_for("index"))
        
if __name__ == "__main__":
	app.debug = True
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)