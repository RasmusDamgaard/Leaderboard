from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import pandas as pd
import numpy as np

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Ranking numbers
results = db.execute("SELECT player, SUM(score) AS points, COUNT(round) AS rounds FROM scores GROUP BY player ORDER BY points DESC")

# Game round scores
rows = db.execute("SELECT b.game_name as Game, a.round as Round, a.timestamp as Date, a.player, a.score as Score \
                FROM scores AS a \
                LEFT JOIN games AS b \
                ON a.game_id = b.game_id")

# Final dataframe
df = pd.DataFrame(rows)

if not df.empty:
    # rearrange game round data for table
    df2 = df.set_index(['Game', 'Round', 'Date', 'player'])['Score'].unstack()
    df3 = df2.reset_index().replace(np.nan, '', regex=True)
else:
    cols = list(df.columns)

cols