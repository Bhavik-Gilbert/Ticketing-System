from flask import Blueprint, redirect, url_for, render_template, request, session, flash

main = Blueprint("main", __name__, static_folder="static", template_folder="template")

import functions
from functions import logged_out

@main.route("/logout/")
def logout():
    session.clear()
    session.permanent = False
    flash("Logout successful")
    return redirect(url_for("start.login"))
