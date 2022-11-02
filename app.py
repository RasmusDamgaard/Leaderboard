from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import pandas as pd
import numpy as np

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
#@login_required
def index():
    """ Show rankings """

    # Find overview of available games
    games = db.execute("SELECT * FROM games")

    # Find all players
    players = db.execute("SELECT DISTINCT player FROM scores")

    # Get selected game
    selected_game = request.form.get("game")

    if request.method == "POST":

        # Get selected players
        sel_players = request.form.getlist("selection")
        # print("YOU ARE HERE>>>>>>: ",sel_players)

        if selected_game == "All":

            # I no players are selected
            if not sel_players:

                # Ranking numbers
                results = db.execute("SELECT player, SUM(score) AS points, COUNT(round) AS rounds FROM scores GROUP BY player ORDER BY points DESC")

                # Game round scores
                rows = db.execute("SELECT b.game_name as Game, a.round as Round, a.timestamp as Date, a.player, a.score as Score \
                                FROM scores AS a \
                                LEFT JOIN games AS b \
                                ON a.game_id = b.game_id")

                # Final dataframe
                df = pd.DataFrame(rows)

            # Else only show selected players
            else:

                # Find game id and rounds for selected players to use as filter
                db.execute("INSERT INTO players_tmp SELECT game_id, round FROM scores WHERE player IN (?)", (sel_players))

                db.execute("INSERT INTO scores_tmp SELECT DISTINCT a.round, a.game_id, \
                            b.player, b.score, b.timestamp, b.creator FROM players_tmp AS a LEFT JOIN scores AS b \
                            ON a.game_id = b.game_id AND a.round = b.round")

                results = db.execute("SELECT player, SUM(score) AS points, COUNT(round) AS rounds \
                                    FROM scores_tmp GROUP BY player ORDER BY points DESC")

                # Game round scores
                rows = db.execute("SELECT b.game_name as Game, a.round as Round, a.timestamp as Date, a.player, a.score as Score \
                                FROM scores_tmp AS a LEFT JOIN games AS b ON a.game_id = b.game_id")

                # Empty tmp tables
                db.execute("DELETE FROM players_tmp")
                db.execute("DELETE FROM scores_tmp")

                # Final dataframe
                df = pd.DataFrame(rows)

            if not df.empty:
                # rearrange game round data for table
                df2 = df.set_index(['Game', 'Round', 'Date', 'player'])['Score'].unstack()
                df3 = df2.reset_index().replace(np.nan, '', regex=True)
                cols = list(df3.columns)
            else:
                cols = list(df.columns)

            # Create list of columns and rows for jinja templating
            Row_list =[]

            if not df.empty:
                for row in df3.itertuples(index=False, name=None):
                    Row_list.append(row)

            return render_template("overview_select.html", page="overview_select", games=games, selected_game=None, results=results, cols=cols, rows=Row_list, players=players)

        else:       

            # Find game id
            rows = db.execute("SELECT game_id FROM games WHERE game_name = ?", selected_game)
            game_id = rows[0]["game_id"]
            
            # Game round scores
            rows = db.execute("SELECT b.game_name as Game, a.round as Round, a.timestamp as Date, a.player, a.score as Score \
                            FROM scores AS a \
                            LEFT JOIN games AS b \
                            ON a.game_id = b.game_id \
                            WHERE a.game_id = ?", game_id)
            df = pd.DataFrame(rows)

            if not df.empty:
                # rearrange game round data for table
                df2 = df.set_index(['Game', 'Round', 'Date', 'player'])['Score'].unstack()
                df3 = df2.reset_index().replace(np.nan, '', regex=True)
                cols = list(df3.columns)
            else:
                cols = list(df.columns)

            # Create list of columns and rows for jinja templating
            Row_list =[]

            if not df.empty:
                for row in df3.itertuples(index=False, name=None):
                    Row_list.append(row)

            results = db.execute("SELECT player, SUM(score) AS points, COUNT(round) AS rounds FROM scores WHERE game_id = ? GROUP BY player ORDER BY points DESC", game_id)

            return render_template("overview_select.html", page="overview_select", games=games, selected_game=selected_game, results=results, cols=cols, rows=Row_list, players=players)

    else:

        # If not selected game or players 
        # Game round scores
        rows = db.execute("SELECT b.game_name as Game, a.round as Round, a.timestamp as Date, a.player, a.score as Score \
                        FROM scores AS a \
                        LEFT JOIN games AS b \
                        ON a.game_id = b.game_id")
        df = pd.DataFrame(rows)

        if not df.empty:
            # rearrange game round data for table
            df2 = df.set_index(['Game', 'Round', 'Date', 'player'])['Score'].unstack()
            df3 = df2.reset_index().replace(np.nan, '', regex=True)
            cols = list(df3.columns)
        else:
            cols = list(df.columns)

        # Create list of columns and rows for jinja templating
        Row_list =[]

        if not df.empty:
            for row in df3.itertuples(index=False, name=None):
                Row_list.append(row)

        results = db.execute("SELECT player, SUM(score) AS points, COUNT(round) AS rounds FROM scores GROUP BY player ORDER BY points DESC")

        return render_template("overview.html", page="overview", games=games, selected_game=None, results=results, cols=cols, rows=Row_list, players=players)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Logged In!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", page="login")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged Out!")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If post request show user register form
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check for possible errors
        if not username:
            return apology("must provide username", 400)

        elif not password:
            return apology("must provide password", 400)

        elif not confirmation:
            return apology("must confirm password", 400)

        elif password != confirmation:
            return apology("passwords does not match", 400)

        # check if user already exists
        user_exist = db.execute("SELECT username FROM users WHERE username = ?", username)
        if user_exist:
            return apology("User already exists", 400)

        # Hash password
        hash = generate_password_hash(password)

        # Insert user into SQL table
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Log user in
        flash("Successfully Registered!")
        return redirect("/login")

    else:

        return render_template("register.html", page="register")


@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    """Add game to database"""

    if request.method == "POST":

        # Manipulate input
        title = request.form.get("title") 
        playercount = request.form.get("playercount")

        # remove leading and trailing whitespace and lower case
        title = title.strip().lower().replace("_"," ")

        # make first char in each word uppercase
        title = title.title()

        # Check if game already exists
        rows = db.execute("SELECT game_name FROM games WHERE game_name = ?", title)
        if len(rows) != 0:
            return apology("Game already exists", 403)

        # Get userid
        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        creator = user[0]["username"]

        # Insert into table
        db.execute("INSERT INTO games (game_name, player_count, creator) VALUES (?,?,?)", title, playercount, creator)

        # Redirect to homepage
        flash("Game Added to Database!")
        return redirect("/")

    else:

        # Render page
        return render_template("game.html", page="game")


@app.route("/score", methods=["GET", "POST"])
@login_required
def score():
    """Add score to database"""

    if request.method == "GET":

        # Find overview of available games
        games = db.execute("SELECT * FROM games")

        # Render page
        return render_template("score.html", page="score", games=games, selected_game=None, player_count=None)
    
    else:

        # If already selected game and added players then update db
        if request.form.get("name_1") == None or request.form.get("name_1") == "":

            # Else find overview of available games
            games = db.execute("SELECT * FROM games")

            # Get selected game
            selected_game = request.form.get("game") 

            # Find player count
            rows = db.execute("SELECT player_count FROM games WHERE game_name = ?", selected_game)
            player_count = rows[0]["player_count"]

            # Render page
            return render_template("score.html", page="score", games=games, selected_game=selected_game, player_count=player_count)

        else:

            # Get selected game
            selected_game = request.form.get("game") 

            # Find player count
            rows = db.execute("SELECT player_count FROM games WHERE game_name = ?", selected_game)
            player_count = rows[0]["player_count"]

            # Find game id
            rows = db.execute("SELECT game_id FROM games WHERE game_name = ?", selected_game)
            gameid = rows[0]["game_id"]

            # Find round number
            max_r = db.execute("SELECT MAX(round) AS max_round FROM scores WHERE game_id = ?", gameid)

            if max_r[0]["max_round"] == None:
                round = 1
            else:
                round = int(max_r[0]["max_round"])
                round += 1

            # Find date
            date = request.form.get("date")

            # simple date validation
            if len(date) not in (10, 9):
                return apology("Date must be of format DD/MM/YYYY", 400)

            if date[2] != "/":
                return apology("Date must be of format DD/MM/YYYY", 400)

            if date[5] != "/":
                return apology("Date must be of format DD/MM/YYYY", 400)


            # Get userid
            user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
            creator = user[0]["username"]

            # Create empty dict to insert in table
            dict = {}

            # Insert player scores into database
            for i in range(player_count):
                name = request.form.get("name_" + str(i))
                score = request.form.get("score_" + str(i))

                # remove leading and trailing whitespace and lower case
                name = name.strip().lower().replace("_"," ")

                # make first char in each word uppercase
                name = name.title()

                # Insert into dict
                dict[name] = score

            # Filter out empty names and scores
            print(dict)
            dict_clean = {k: v for k, v in dict.items() if v}
            print(dict_clean)

            for x, y in dict_clean.items():
                db.execute("INSERT INTO scores (round, game_id, player, score, timestamp, creator) VALUES (?, ?, ?, ?, ?, ?)", round, gameid, x, y, date, creator)

            # Redirect to homepage
            flash("Score Added to Database!")
            return redirect("/")