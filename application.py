import os

import cs50
from cs50 import SQL, get_string
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# import helper functions
from functions import apology, login_required, confirm_email

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
db = SQL("sqlite:///database.db")


# defining dynamic classes for html via ajax
class1 = "auth"
class2 = "app"


@app.route("/")
def home():
    return redirect("/setup")


@app.route("/login", methods=["GET", "POST"])
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
            return apology("invalid username or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/setup")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# have user select their avatar
@app.route("/avatar", methods=["GET", "POST"])
@login_required
def avatar():

    # log the user id
    userid = session["user_id"]

    # updates user avatar selection in database
    if request.method == "POST":

        avatar = request.form.get("avatar")
        db.execute("UPDATE users SET avatar=:avatar WHERE user_id=:userid", userid=userid, avatar=avatar)
        return redirect("/setup")

    else:
        return render_template("avatar.html", class1=class1)


# main page with question and answers for users to set up for application
@app.route("/setup", methods=["GET", "POST", "DELETE"])
@login_required
def setup():

    # log the user id
    userid = session["user_id"]

    # pulls user interview information if exists
    interview = db.execute("SELECT * FROM interview WHERE user_id = :userid", userid=userid)

    if request.method == "DELETE":

        # deletes question from database if user selects the delete option
        questionid = request.json
        db.execute("DELETE FROM interview WHERE question_id=:questionid", questionid=questionid)
        return jsonify(True)

    elif request.method == "POST":

        # receive array for question and answers from front end
        data = request.json

        first = data[0]["firstname"]
        last = data[0]["lastname"]
        job = data[0]["job"]
        country = data[0]["country"]

        # on submit validate no blanks
        if not first or not last:
            return apology("please fill out first and last name")

        # if user already have previously filled out form just update information
        elif len(interview) > 0:

            # update name and interview information
            db.execute("UPDATE users SET first=:first, last=:last, country=:country, job=:job WHERE user_id = :userid",
                       userid=userid, first=first, last=last, country=country,job=job)

            # for each item in the submitted form, update or insert into database for user
            for i in range(len(data) - 1):
                i += 1
                category = data[i]["category"]
                question = data[i]["question"]
                answer = data[i]["answer"]
                q_id = int(data[i]["id"])

                # update old questions
                if q_id > 0:
                    db.execute("UPDATE interview SET category=:category, question=:question, answer=:answer WHERE question_id=:q_id",
                               q_id=q_id, category=category, question=question, answer=answer)
                # insert new ones
                else:
                    db.execute("INSERT INTO interview(user_id, category, question, answer) values( :userid, :category, :question, :answer)",
                           userid=userid, question=question, answer=answer, category=category)
            return jsonify("/application")

        # for new registrated users without any forms filled before
        else:

            # update name from registration and insert user interview set up input into interview table
            db.execute("UPDATE users SET first=:first, last=:last, country=:country, job=:job WHERE user_id = :userid",
                       userid=userid, first=first, last=last, country=country,job=job)

            for i in range(len(data) - 1):
                i += 1
                category = data[i]["category"]
                question = data[i]["question"]
                answer = data[i]["answer"]


                db.execute("INSERT INTO interview(user_id, question, answer, category) values( :userid, :question, :answer, :category)",
                           userid=userid, question=question, answer=answer, category=category)

            return jsonify("/application")

    # on get, populate all user previous filled out information
    else:

        if len(interview) > 0:

            # pull up the users existing information to populate the form
            content = db.execute("SELECT * FROM users JOIN interview ON users.user_id=interview.user_id WHERE users.user_id=:userid AND interview.user_id=:userid", userid=userid)

            # state variables to populate in form for existing users with their existing information
            first = content[0]["first"]
            last = content[0]["last"]
            job = content[0]["job"]
            country = content[0]["country"]

            # populate the template with existing variables
            return render_template("setup.html", content=content, class1=class1, first=first, last=last, job=job, country=country)

        else:
            return render_template("setup.html", class1=class1)


# Outputted (actual) application - share with interviewers to get your virtual interview
@app.route("/application", methods=["GET", "POST"])
def application():

    # checks if user is logged in or not. Returns user id based on either shareable link or logged in session id
    if session.get("user_id") is None:
        userid = request.args.get("userid")
    else:
        userid = session["user_id"]

    content = db.execute("SELECT * FROM users JOIN interview ON users.user_id=interview.user_id WHERE users.user_id=:userid AND interview.user_id=:userid", userid=userid)
    avatar = content[0]["avatar"]
    first = content[0]["first"]
    last = content[0]["last"]

    if not avatar or not first or not last:
        return apology("please complete set up before coming here")
    else:
        return render_template("application.html", class1=class2, avatar=avatar, content=content, first=first, last=last)


# returns json data over to front end for application
@app.route("/content", methods=["GET"])
def content():

    # checks if user is logged in or not. Returns user id based on either shareable link or logged in session id
    if session.get("user_id") is None:
        userid = request.args.get("userid")
    else:
        userid = session["user_id"]

    content = db.execute("SELECT * FROM users JOIN interview ON users.user_id=interview.user_id WHERE users.user_id=:userid AND interview.user_id=:userid", userid=userid)

    return jsonify(content)


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

        new_user = request.form.get("username")
        pword = request.form.get("password")
        confirm = request.form.get("confirmation")
        email = request.form.get("email")

        # query the database with all user information
        users = db.execute("SELECT * FROM users WHERE username = :username", username=new_user)
        address = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        # ensures validation for mandatory input fields
        if not new_user:
            return apology("missing username")
        elif not pword:
            return apology("missing password")
        elif not confirm:
            return apology("must confirm password")
        elif not email:
            return apology("Please input email")
        # check if username already exists
        elif len(users) >= 1:
            return apology("Username Taken")
        # checks for taken email
        elif len(address) >=1:
            return apology("Email already registered")
        # ensure password confirmation is valid
        elif pword != confirm:
            return apology("Passwords do not match")
        else:
            # add new user into database
            hash_p = generate_password_hash(pword)
            db.execute(
                "INSERT INTO users(username, hash, email) values(:username, :hash, :email)",
                  username=new_user, hash=hash_p, email=email)

            # reload users after insert
            users = db.execute("SELECT user_id FROM users WHERE username = :username", username=new_user)

            # saves the session for this user
            session["user_id"] = users[0]["user_id"]
            userid = session["user_id"]

            # sends confirmation email to user and redirects to avatar selection #
            # uses SendGrid free account and API to send email #
            return confirm_email(new_user, userid, email)

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
    # checks if username or email already exists
    if len(users) >= 1:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/share", methods=["GET"])
@login_required
def share():
    userid = session["user_id"]
    return render_template("share.html", userid=userid, class1=class2)

@app.route("/faq", methods=["GET"])
def faq():
    return render_template("faq.html", class1=class2)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)