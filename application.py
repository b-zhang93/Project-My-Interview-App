import os

import cs50
from cs50 import SQL, get_string
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib

from functions import apology, login_required

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


# DATABASE FUNCTIONALITIES HERE
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/login", methods=["Get", "POST"])
def login():

    # Forget any user
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/setup")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# main page with question and answers for users to set up for application
@app.route("/setup", method=["POST", "GET"])
@login_required
def setup():

    # log the user id
    userid = session["user_id"]

    # pulls user interview information if exists
    interview = db.execute("SELECT * FROM interview WHERE id = :userid", userid=userid)

    if request.method == "POST":

        first = request.form.get("firstname")
        last = request.form.get("lastname")
        questions = request.form.get("questions")
        answers = request.form.get("answers")
        categories = request.form.get("categories")

        # on submit validate no blanks
        if not first or not last:
            return apology("please fill out first and last name")
        elif not questions or not answers or not categories:
            return apology("please fill in Q/A and category")

        # if user already have previously filled out form just update information
        elif len(interview) > 0:

            # update name and interview information
            db.execute("UPDATE users SET first=:first, last=:last WHERE id = :userid", userid=userid, first=first, last=last)
            db.execute("UPDATE interview SET question=:questions, answer=:answers, category=:categories WHERE id = :userid",
                       userid=userid, questions=questions, answers=answers, categories=categories)

            return redirect("/application")

        # if new user do a competely new set up and insert information into database
        else:

            # update name from registration and insert user interview set up input into interview table
            db.execute("UPDATE users SET first=:first, last=:last WHERE id = :userid", userid=userid, first=first, last=last)
            db.execute("INSERT INTO interview(id, question, answer, category) values( :userid, :questions, :answers, :categories)",
                       userid=userid, questions=questions, answers=answers, categories=categories)

            return redirect("/application")

    else:

        if len(interview) > 0:

            # populate form text with previous information from INTERVIEW variable
            return render_template("setup.html", interview=interview)

        else:
            return render_template("setup.html", interview=interview)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


# REGISTER STUFF HERE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        firstn = request.form.get("firstname")
        lastn = request.form.get("lastname")
        new_user = request.form.get("username")
        pword = request.form.get("password")
        confirm = request.form.get("confirmation")
        email = request.form.get("email")
        country = request.form.get("country")
        job = request.form.get("job")

        # query the database with all user information
        users = db.execute("SELECT * FROM users WHERE username = :username", username=new_user)

        # ensures validation for mandatory input fields
        if not new_user:
            return apology("missing username")
        elif not pword:
            return apology("missing password")
        elif not confirm:
            return apology("must confirm password")
        elif not firstn or not lastn:
            return apology("Must Have First and Last Name")
        elif not email:
            return apology("Please input email")

        # check if username already exists
        elif len(users) >= 1:
            return apology("Username Taken")
        # ensure password confirmation is valid
        elif pword != confirm:
            return apology("Passwords do not match")

        # add new user into database
        else:
            hash_p = generate_password_hash(pword)
            db.execute(
                "INSERT INTO users(username,hash,email,job,country,first,name) values(:username, :hash, :email, :job, :country, :firstn, :lastn)",
                  username=new_user, hash=hash_p, email=email, job=job, country=country, firstn=firstn, lastn=lastn)

            # sends confirmation email to user
            message = "You are registered!"
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("jharvard@cs50.net", os.getenv("PASSWORD"))
            server.sendmail("jharvard@cs50.net", email, message)

            # redundant?
            users = db.execute("SELECT * FROM users WHERE username = :username", username=new_user)

            # saves the session for this user
            session["user_id"] = users[0]["id"]

            return redirect("/setup")
    else:
        return render_template("register.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    user = request.args.get("username")
    # query the database with IDs and usernames
    users = db.execute("SELECT * FROM users WHERE username = :username", username=user)

    # ensures validation for username
    if not user:
        return jsonify(False)

    # checks if username already exists or not
    if len(users) >= 1:
        return jsonify(False)

    else:
        return jsonify(True)


# EMBEDDED LINK OR OUTPUT VERSION (ACTUAL APPLICATION)
@app.route("/application", methods=["GET"])
@login_required
def application():

    userid = session["user_id"]

    ### auto-log-in based on unique link###
    # ##functionalities based on interactions with app? (figure this part out) ##

    # select necessary dictionary with join function
    content = db.execute(
        "SELECT first, last, question, answer, category FROM users JOIN interview ON users.id=interview.id WHERE userid=:userid", userid=userid)

    ### how do i send content over to HTML side? ###

    return render_template("application.html", dictionary=content)



### how to password reset #### ??
# @app.route("/reset", methods=["POST", "GET"])

#     if request.method == "POST":
#         # reset password form




#     else:


#         return render_template("reset.html")
### complicated or simple way? ###




# ERROR HANDLER ETC>>

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)