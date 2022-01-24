from pprint import isrecursive
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from mysqlx import Session
from numpy import record
from functions import query, logged_out, empty, valid_email, password_check as valid_password, logged_in, get_hashed_password as hash, check_password as check_hash
from connection import query

user = Blueprint("user", __name__, static_folder="static", template_folder="template")

@user.route("/", methods=["POST", "GET"])
def account():
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (session["id"],)
    user = query("""SELECT Email, Name, Username FROM user
                    WHERE UserID = %s""", record)
    
    groups = query("""SELECT GroupName, GroupDescription FROM groups
                      WHERE Owner = %s""", record)
    
    projects = query("""SELECT ProjectName, ProjectDescription FROM projects
                      WHERE Manager = %s""", record)

    record = (session["id"], False)
    tickets_started = query("""SELECT TicketName, TicketDescription FROM tickets
                      WHERE UserID = %s AND Completed = %s""", record)
    
    record = (session["id"], True)
    tickets_completed = query("""SELECT TicketName, TicketDescription, DateCompleted FROM tickets
                      WHERE UserID = %s AND Completed = %s""", record)

    if(empty(groups)):
        groups = []
    if(empty(projects)):
        projects = []
    if(empty(tickets_started)):
        tickets_started = []
    if(empty(tickets_completed)):
        tickets_completed = []

    return render_template("Account/account.html", user = user[0], groups = groups, projects = projects, tickets_started = tickets_started, tickets_completed = tickets_completed, 
                            group_num = len(groups), project_num = len(projects), tstart_num = len(tickets_started), tcomplete_num = len(tickets_completed))

@user.route("/edit_account/", methods=["POST", "GET"])
def edit_account():
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (session["id"],)
    user = query("""SELECT Email, Name, Username FROM user
                    WHERE UserID = %s""", record)
    
    Name = user[0][1].split(" ")

    message = ""
    if request.method == "POST":
        firstname = request.form["Firstname"]
        surname = request.form["Surname"]
        name = request.form["Firstname"] + " " + request.form["Surname"]
        email = request.form["Email"]
        password = request.form["Password"]
        confirm_password = request.form["Confirm_Password"]
        current_password = request.form["Current_Password"]

        record = (session["id"],)
        select_password = query("""SELECT Password FROM user WHERE UserID = %s""", record)
        password_check = check_hash(current_password, hashed_password=select_password[0][0])

        try:
            captcha = request.form['captcha']
            captcha = True
        except:
            captcha = False

        if not(captcha):
            message += "Invalid captcha<br>"
        if(empty(firstname) or empty(surname) or empty(email) or empty(password) or empty(confirm_password) or empty(current_password)):
            message += "Please fill in all fields<br>"
        if(name.isnumeric()):
           message += "Please enter a valid name<br>" 
        if not(valid_email(email)):
             message += "Please enter a valid email<br>" 
        if not(confirm_password == password):
            message += "The passwords do not match<br>"
        if not valid_password(password):
            message += "Password is not strong enough<br>"

        if not(password_check):
            message = "Invalid current password"

        if(empty(message)):
            password = hash(password)
           
            record = (name, email, password, session["id"])
            query("""UPDATE user
                     SET name=%s, Email=%s, Password=%s
                     WHERE UserID=%s""", record)
                
            flash("Details changed successfully")
            return redirect(url_for("user.account"))

    return render_template("Account/edit_account.html", Email = user[0][0], Username = user[0][2], Firstname = Name[0], Surname = Name[1],
                            message=message, showMessage = not empty(message))
    
@user.route("/delete_account/", methods=["POST", "GET"])
def delete_account():
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (session["id"],)
    owner = query("""SELECT * FROM groups
                     WHERE Owner = %s""", record)
    manager = query("""SELECT * FROM projects
                     WHERE Manager = %s""", record)

    if not(empty(manager) & empty(owner)):
        flash("You can't delete this account, there are groups owned by or projects run by this account")
        flash("Transfer all duties before attempting to delete an account")
        return redirect(url_for("user.account"))
    
    record = (None, session["id"])
    query("""UPDATE tickets
             SET UserID=%s
             WHERE UserID=%s""", record)

    record = (session["id"],)
    query("""DELETE FROM projectlist
             WHERE UserID=%s""", record)
    query("""DELETE FROM memberlist
             WHERE UserID=%s""", record)
    query("""DELETE FROM user
             WHERE UserID=%s""", record)

    flash("Account deleted successfully")
    return redirect(url_for("main.logout"))