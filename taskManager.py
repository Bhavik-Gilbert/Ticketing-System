from flask import Flask, redirect, url_for, render_template, request

from datetime import timedelta

from group import group
from start import start
from main import main
from projects import project
from tickets import tickets
from account import user

app = Flask(__name__)

app.secret_key = "top task"
app.permanent_session_lifetime = timedelta(minutes=60)

app.register_blueprint(start, url_prefix="")
app.register_blueprint(main, url_prefix="")
app.register_blueprint(group, url_prefix="/groups")
app.register_blueprint(project, url_prefix="/projects")
app.register_blueprint(tickets, url_prefix="/tickets")
app.register_blueprint(user, url_prefix="/account")

if __name__ == "__main__":
    app.run(debug=True)