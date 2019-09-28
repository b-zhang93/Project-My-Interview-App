import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# source: www.sendgrid.com free account with web API to send emails without having to input password (check requirements.txt)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class3 = "error"

# github may have their own error pages ... so might not need this or simplify to be simpler
def apology(message):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", bottom=escape(message), class1=class3)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# sending emails with SendGrid (requirements.txt)
def confirm_email(user, userid, email):

    message = Mail(
        from_email='myinterviewapp@gmail.com',
        to_emails= email,
        subject='My Interview App Registration',
        html_content=f'You are now registered! Your username is <strong>{user}</strong> and your <strong>user ID is {userid}</strong>. Remember these for now!')
    try:

        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

        return redirect("/avatar")

    except:
        return apology("Email Send Error Try Again")

