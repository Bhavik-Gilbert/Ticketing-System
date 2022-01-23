from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from functions import logged_out, empty

user = Blueprint("user", __name__, static_folder="static", template_folder="template")

@user.route("/", methods=["POST", "GET"])
def account():
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    return render_template("Account/account.html")