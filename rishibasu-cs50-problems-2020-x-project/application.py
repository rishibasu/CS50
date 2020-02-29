import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

import random

from helpers import apology

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.1.db")



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/players", methods=["GET", "POST"])
def players():
    """Let user enter players for the tournament"""
    if request.method == "POST":

        for b in range(30):
            idname= 't'+ str(b)

            names=request.form.get(str(idname))
            point=b+1
            if names:
                nam=str(names)
                db.execute("INSERT into Players (name, id, rank) VALUES (:namey, :id, :rank)", namey=nam, id=b, rank=point)


        return redirect("/scores")
    elif request.method == "GET":
        return render_template ("players.html")




@app.route("/pairings", methods=["GET", "POST"])
#@login_required
def pairings():
    #current_round
    """Show pairings of players"""
    games=db.execute("SELECT COUNT (*) FROM Players")
    gamesy = games[0]["COUNT (*)"]
    rows = gamesy / 2
    n=int(rows)
    users=int(gamesy)
    if request.method == "POST":
        """save the results"""
        for x in range(n):
            win=str(x)
            winner=request.form.get(win)
            board = int(x) + 1
            """winner has 3 values"""
            #universal names
            nameofwhite=db.execute("SELECT white from matchups WHERE board=:board", board=board)
            whitename=nameofwhite[0]["white"]
            nameofblack=db.execute("SELECT black from matchups WHERE board=:board", board=board)
            blackname=nameofblack[0]["black"]
            #scorelists (points) for white/black
            scoreofwhite=db.execute("SELECT score FROM Players WHERE Name=:name", name=whitename)
            scoreofblack=db.execute("SELECT score FROM Players WHERE Name=:name", name=blackname)
            #scorelists (opponent_points) for white/black
            whiteop=db.execute("SELECT opponent_points FROM Players WHERE Name=:white", white=whitename)
            blackop=db.execute("SELECT opponent_points FROM Players WHERE Name=:black", black=blackname)

            if winner == 'option1':
                #match result
                db.execute("UPDATE matchups SET result = :result WHERE board=:board", result=1, board=board)

                #white score update
                scorew=scoreofwhite[0]["score"] + 1
                db.execute("UPDATE Players SET score=:result WHERE Name=:name", result=scorew, name=whitename)

                #black opponent_points update
                scorebop=blackop[0]["opponent_points"]+1
                db.execute("UPDATE Players SET opponent_points=:result WHERE Name=:name", result=scorebop, name=blackname)



            elif winner == 'option2':
                #match result
                db.execute("UPDATE matchups SET result = :result WHERE board=:board", result=0, board=board)

                #black score update
                scoreb=scoreofblack[0]["score"] + 1
                db.execute("UPDATE Players SET score=:result WHERE Name=:name", result=scoreb, name=blackname)

                #white opponent_points update
                scorewop=whiteop[0]["opponent_points"]+1
                db.execute("UPDATE Players SET opponent_points=:result WHERE Name=:name", result=scorewop, name=whitename)


            elif winner == 'option3':
                #match result
                db.execute("UPDATE matchups SET result = :result WHERE board=:board", result=0.5, board=board)

                #white score update
                scorew=scoreofwhite[0]["score"] + 0.5
                db.execute("UPDATE Players SET score=:result WHERE Name=:name", result=scorew, name=whitename)

                #black score update
                scoreb=scoreofblack[0]["score"] + 0.5
                db.execute("UPDATE Players SET score=:result WHERE Name=:name", result=scoreb, name=blackname)


                #update white opponent_points
                scorewop=whiteop[0]["opponent_points"]+0.5
                db.execute("UPDATE Players SET opponent_points=:result WHERE Name=:name", result=scorewop, name=whitename)

                #update black opponent_points
                scorebop=blackop[0]["opponent_points"] +0.5
                db.execute("UPDATE Players SET opponent_points=:result WHERE Name=:name", result=scorebop, name=blackname)

        #change aggregate
        #users=int(gamesy)
        data=db.execute("SELECT * FROM Players")
        for c in range(users):
            namer=data[c]["Name"]
            points=data[c]["score"]
            opps=data[c]["opponent_points"]
            aggregate = points*50 + opps*2
            db.execute("UPDATE Players SET aggregate=:aggregate WHERE Name=:name", aggregate=aggregate, name=namer)


        #change ranks (works like a charm)
        list=db.execute("SELECT * FROM Players ORDER BY aggregate DESC")
        for a in range(users):
            y=int(a)
            name=list[y]["Name"]
            a=a+1
            db.execute("UPDATE Players SET rank=:rank WHERE Name=:name", rank=a, name=name)



        return redirect("/scores")

    else:
        boards=1
        """all the work I need to do goes here I believe"""

        current = db.execute("SELECT round FROM matchups")

        if not current:
            current_round=1
        else:
            rounds=current[0]["round"]
            current_round=rounds+1
            #erase matchups data
            db.execute("DELETE FROM matchups")

        if current_round == 1:
            opponents=db.execute("SELECT Name FROM Players")
            whites=db.execute("SELECT Name FROM Players WHERE id<:id", id=rows)
            db.execute("UPDATE Players SET color=:color WHERE id<:id", color=1, id=rows)
            blacks=db.execute("SELECT Name FROM Players WHERE id>=:id", id=rows)
            db.execute("UPDATE Players SET color=:color WHERE id>=:id", color=0, id=rows)
            for a in range(int(rows)):
                whiteplayer=whites[a]["Name"]
                blackplayer=blacks[a]["Name"]
                board=int(a) + 1
                db.execute("INSERT into matchups (board,round, white, black) VALUES (:board, :roundy, :white, :black)", board=board, roundy=1, white=whiteplayer, black=blackplayer)
            pairing=db.execute("SELECT * FROM matchups")

            return render_template("pairings.html", n=n, current_round=current_round, pairing=pairing)

        #next pairings
        elif current_round == 2 or 3 or 4:
            info=db.execute("SELECT * FROM Players ORDER BY rank")
            for a in range(1,users,2):

                b=a+1
                c=a-1
                acolor=info[c]["color"]
                bcolor=info[a]["color"]
                #get names
                up=info[c]["Name"]
                down=info[a]["Name"]

                if acolor==bcolor:
                    high=random.randint(0,1)
                    low=1-high
                    #change color in pairings
                    db.execute("UPDATE Players SET color=:color WHERE rank=:rank", color=high, rank=a)
                    db.execute("UPDATE Players SET color=:color WHERE rank=:rank", color=low, rank=b)
                    #get the right names
                    if high ==1:
                        whitename=up
                        blackname=down
                    else:
                        whitename=down
                        blackname=up
                    #insert new row into matchups
                    db.execute("INSERT into matchups (board, round, white, black) VALUES (:board, :roundy, :white, :black)", board=boards, roundy=current_round, white=whitename, black=blackname)
                else:
                    acolor = 1-acolor
                    bcolor= 1-bcolor
                    db.execute("UPDATE Players SET color=:color WHERE rank=:rank", color=acolor, rank=a)
                    db.execute("UPDATE Players SET color=:color WHERE rank=:rank", color=bcolor, rank=b)
                    if acolor==1:
                        db.execute("INSERT into matchups (board, round, white, black) VALUES (:board, :roundy, :white, :black)", board=boards, roundy=current_round, white=up, black=down)
                    else:
                        db.execute("INSERT into matchups (board, round, white, black) VALUES (:board, :roundy, :white, :black)", board=boards, roundy=current_round, white=down, black=up)
                boards=boards+1

            pairing=db.execute("SELECT * FROM matchups")
            return render_template("pairings.html", n=n, current_round=current_round, pairing=pairing)

        elif current_round >=5:
            return redirect("/history")
           # select=db.execute("SELECT * FROM Players ORDER BY rank DESC")
           # winnername=select[0]["Name"]
           # return render_template("history.html", winnername=winnername)


@app.route("/history")
#@login_required
def history():
    """Celebration page for the winner"""
    if request.method == "GET":
        nowplay=db.execute("SELECT * FROM Players ORDER BY rank")
        winnerguy=str(nowplay[0]["Name"])
        return render_template("history.html", winnerguy=winnerguy)



@app.route("/scores", methods=["GET", "POST"])
#@login_required
def scores():

    """Rank players based on their current scores"""
    if request.method == "GET":
        now=db.execute("SELECT round FROM matchups")
        if now:
            nowis=now[0]["round"]
            if nowis>=4:
                message='End'

            else:
                message='Get Pairings'
        else:
            message='Get Pairings'
        for c in range(30):
            leaderboard = db.execute("SELECT * FROM Players ORDER BY rank")
            return render_template("scores.html", leaderboard=leaderboard, message=message)

    elif request.method == "POST":
        now=db.execute("SELECT round FROM matchups")
        if now:
            nowis=now[0]["round"]
            if nowis>=4:
                return redirect("/history")

        return redirect("/pairings")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)






