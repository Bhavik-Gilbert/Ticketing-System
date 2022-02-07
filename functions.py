import re
import bcrypt
from flask import session, flash, request

from connection import query

def valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if(re.fullmatch(regex, email)):
        return True
    return False

def password_check(password: str):
    try:
        # calculating the length
        length_error = len(password) < 8

        # searching for digits
        digit_error = re.search(r"\d", password) is None

        # searching for uppercase
        uppercase_error = re.search(r"[A-Z]", password) is None

        # searching for lowercase
        lowercase_error = re.search(r"[a-z]", password) is None

        # searching for symbols
        symbol_error = re.search(r"[ @!#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

        # overall result
        password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )
    except:
        password_ok = False

    return password_ok

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    #password can be up to 72 chars
    return bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))

def empty(text):
    if(len(text)>0):
        return False
    return True

def logged_out():
    if not(session.permanent):
        flash("Log in to access rest of site")
        return True
    return False

def logged_in():
    if (session.permanent):
        flash("Already logged in")
        return True
    print(session.permanent)
    return False

def group_check(number, id):
    record = ( number, id)
    user_access = query("""SELECT Accepted FROM memberlist
                            WHERE GroupID = %s AND UserID = %s""", record)
    try:
        if not(user_access[0][0]):
            flash("You are not in this group, receive and accept an invite to get access to this space")
            return False
    except:
        flash("You are not in this group, receive and accept an invite to get access to this space")
        return False
    
    return True

def project_check(number, id):
    record = ( number, id)
    user_access = query("""SELECT * FROM projectlist
                            WHERE ProjectID = %s AND UserID = %s""", record)
    print(user_access)
    try:
        if not(user_access[0][0]):
            flash("You are not on this project, enter the project to get access to this space")
            return False
    except:
        flash("You are not on this project, enter the project to get access to this space")
        return False
    
    return True

def owner_check(owner_id, accept:str, decline:str, error:str):
    try:
        owner = owner_id    
        if(owner == session["id"]):
            flash(accept)
            return True
        else:
            flash(decline)
            return False
    except:
        flash(error)
        return None;

