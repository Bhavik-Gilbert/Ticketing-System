from flask import Flask, redirect, url_for, render_template, request
import git
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

@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('path/to/git_repo')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

if __name__ == "__main__":
    app.run(debug=True)