from flask import Blueprint, redirect, url_for, render_template, request, session, flash

from functions import empty, valid_email, password_check as valid_password, logged_in, get_hashed_password as hash, check_password as check_hash

from connection import query

start = Blueprint("start", __name__, static_folder="static", template_folder="template")

@start.route("/", methods=["POST", "GET"])
def login():
    if(logged_in()):
        return redirect(url_for("group.groups"))

    message = ""
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]

        try:
            captcha = request.form['captcha']
            captcha = True
        except:
            captcha = False

        record = (username,)
        select_login = query("""SELECT UserID,Username,Password FROM user WHERE Username = %s""", record)
        try:
            username_check = not empty(select_login)
            password_check = check_hash(password, hashed_password=select_login[0][2])
            
        except:
            username_check = password_check = False

        if not(captcha):
            message += "Invalid captcha<br>"
        if(empty(username) or empty(password)):
            message += "Please fill in all fields<br>"
        if not(username_check and password_check):
            message += "Invalid username or password<br>"
        if(empty(message)):
            session.permanent = True
            session["id"] = select_login[0][0]
            session["user"] = username
            flash("Login successful")
            return redirect(url_for("group.groups"))

    return render_template("Start/index.html" , message=message, showMessage = not empty(message))

@start.route("/signup/", methods=["POST", "GET"])
def signup():
    if(logged_in()):
        return redirect(url_for("group.groups"))

    message = ""
    if request.method == "POST":
        firstname = request.form["Firstname"]
        surname = request.form["Surname"]
        name = request.form["Firstname"] + " " + request.form["Surname"]
        email = request.form["Email"]
        username = request.form["Username"]
        password = request.form["Password"]


        record = (username,)
        select_username = query("""SELECT Username FROM user WHERE Username = %s""", record)
        try:
            double_username = not empty(select_username)
        except:
            double_username = False

        try:
            captcha = request.form['captcha']
            captcha = True
        except:
            captcha = False

        if not(captcha):
            message += "Invalid captcha<br>"
        if(empty(firstname) or empty(surname) or empty(email) or empty(username) or empty(password)):
            message += "Please fill in all fields<br>"
        if(name.isnumeric()):
           message += "Please enter a valid name<br>" 
        if not(valid_email(email)):
             message += "Please enter a valid email<br>" 
        if not valid_password(password):
            message += "Password is not strong enough<br>"
        if(double_username):
            message += "This username is already registered in the system<br>"
        if(empty(message)):
            password = hash(password)
           
            record = (email, name, username, password)
            query("""
                INSERT INTO
                user (Email, Name, Username, Password)
                VALUES
                (%s, %s, %s, %s);
                """,
                record)
                
            flash("Signup successful")
            return redirect(url_for("start.login"))
    
    return render_template("Start/signup.html" , message=message, showMessage = not empty(message))
