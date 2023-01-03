from flask import Blueprint, redirect, url_for, render_template, request, session, flash

group = Blueprint("group", __name__, static_folder="static", template_folder="template")

from functions import logged_out, empty, group_check, owner_check


from connection import query

@group.route("/", methods=["POST", "GET"])
def groups():
    """
    Lists all groups the user is a member of
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    user = session["id"]
    record = (user,)
    select_group = query("""SELECT * FROM groups INNER JOIN memberlist
                            ON groups.GroupID = memberlist.GroupID
                            WHERE UserID = %s""", record)
    

    accepted_list = []
    for group in select_group:
        if (group[6] == True) or (group[6] == 1):
            accepted_list.append(group)

    owners = []
    for group in accepted_list:
        record = (group[3],)
        select_owner = query("""SELECT Username FROM user
                                WHERE UserID=%s""", record)
        owners.append(select_owner[0][0])

    return render_template("Groups/groups.html", groups = accepted_list, user_id=session["id"], owners=owners, list_length = len(owners))

@group.route("/invite/<number>", methods=["POST", "GET"])
def invite_group(number):
    """
    Allows owners to invite users into a group
    Provides search functionality to search through users
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    accept = ""
    deny = "Only the owner of a group can invite someone"
    error = "Failed to access people"
    is_owner = owner_check(session["id"], accept, deny, error)  
    if not(is_owner):
        return redirect(url_for("group.groups"))
        
    
    record = (number,)
    select_members = query("""SELECT UserID FROM groups INNER JOIN memberlist
                            ON groups.GroupID = memberlist.GroupID
                            WHERE memberlist.GroupID = %s""", record)

    if request.method == "POST":
        search = "%"+request.form["Search"]+"%"
        record = (search, search)
        select_people = query("""SELECT UserID, Username FROM user
                                WHERE Username LIKE %s OR Name LIKE %s""", record)
    else:
        select_people = query("""SELECT UserID, Username FROM user""")

    member_id = []
    for member in select_members:
        member_id.append(member[0])

    invite_list = []
    for user in select_people:
        if not (user[0] in member_id):
            invite_list.append(user)
    
    return render_template("Groups/invite.html", invite_list=invite_list, group_id = number)

@group.route("/invite/<number>/invite/<user>", methods=["GET"])
def group_invite(number, user):
    """
    Allows owners to send invites to users
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    accept = "Invite sent"
    deny = "Only the owner of a group can invite someone"
    error = "Failed to send invite"
    is_owner = owner_check(session["id"], accept, deny, error)  
    if (is_owner):
        pass
    else:
        return redirect(url_for("group.groups"))

    record = (number, user)
    query("""INSERT INTO memberlist (GroupID, UserID)
            VALUES(%s, %s);""", record)

    return redirect(url_for("group.groups"))

@group.route("/remove/<number>/remove/<user>", methods=["GET"])
def group_remove(number, user):
    """
    Allows owners to remove members from a group
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    accept = ""
    deny = "Only the owner of a group can remove someone"
    error = "Failed to remove user"
    is_owner = owner_check(session["id"], accept, deny, error) 

    accept ="User Removed"
    deny = "You cannot remove the owner from a group"
    user_owner =  owner_check(int(user), deny, accept, error)
   
    if (not is_owner) | (user_owner):
        return redirect(url_for("group.groups"))


    record = (number, user)
    query("""DELETE FROM memberlist
             WHERE GroupID = %s AND UserID = %s""", record)

    return redirect(url_for("group.groups"))

@group.route("/change/<number>/owner/<user>", methods=["GET"])
def group_change_ownership(number, user):
    """
    Allows owners to transfer ownership of a group
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    accept = ""
    deny = "Only the owner of a group can transfer ownership"
    error = "Failed to transfer ownership"
    is_owner = owner_check(session["id"], accept, deny, error) 

    accept ="Ownership transferred"
    deny = "You cannot transfer ownership to the current owner"
    user_owner =  owner_check(int(user), deny, accept, error)
   
    if (not is_owner) | (user_owner):
        return redirect("/projects/"+number)


    record = (int(user), number)
    query("""UPDATE groups
            SET Owner=%s
            WHERE GroupID=%s""", record)

    return redirect("/projects/"+number)

@group.route("/leave/<number>/", methods=["GET"])
def leave_group(number):
    """
    Allows users to leave a group
    """

    if(logged_out()):
        return redirect(url_for("start.login"))  
    
    record = (number,)
    select_group = query("""SELECT Owner, GroupName FROM groups
                            WHERE GroupID = %s""", record)

    accept = "The owner cannot leave a group. Transfer ownership before trying to leave"
    deny = "You have successfully left " + select_group[0][1]
    error = "Failed to delete group"
    is_owner = owner_check(select_group[0][0], accept, deny, error)  
    if not (is_owner):
        record = (number, session["id"])
        query(""" DELETE FROM memberlist 
            WHERE GroupID = %s AND UserID = %s""", record)
    
    return redirect(url_for("group.groups"))  

@group.route("/delete/<number>", methods=["GET"])
def delete_group(number):
    """
    Allows owners to delete a group
    """

    if(logged_out()):
        return redirect(url_for("start.login"))  
    
    record = (number,)
    select_group = query("""SELECT Owner, GroupName FROM groups
                            WHERE GroupID = %s""", record)
    
    owner = select_group[0][0]    
    if (owner == session["id"]):
        record = (number,)
        query(""" DELETE FROM memberlist 
            WHERE GroupID = %s""", record)

        get_projects = query("""SELECT ProjectID FROM projects 
                            WHERE GroupID=%s""", record)

        for project_ID in get_projects:
            record = (project_ID[0],)

            query(""" DELETE FROM tickets 
                WHERE ProjectID = %s""", record)

            query(""" DELETE FROM projectlist 
                WHERE ProjectID = %s""", record)
            
            query(""" DELETE FROM projects 
                WHERE ProjectID = %s""", record)

        record = (number,)
        query(""" DELETE FROM groups 
            WHERE GroupID = %s""", record)
        
        
        

        flash("You have successfully delete the group" , select_group[0][1])
    else:
        flash("Only the owner can delete a group")
    
    return redirect(url_for("group.groups"))  

@group.route("/invitations/", methods=["GET"])
def invitations():
    """
    Allows users to view their group invitations
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (session["id"],)
    select_group = query("""SELECT memberlist.GroupID, Accepted, GroupName, GroupDescription, Username FROM memberlist 
                            INNER JOIN groups
                            ON memberlist.GroupID = groups.GroupID
                            INNER JOIN user
                            ON groups.Owner = user.UserID
                            WHERE memberlist.UserID = %s""", record)

    invite_list = []
    for group in select_group:
        if (group[1] == False) or (group[1] == 0):
            invite_list.append(group)
    
    return render_template("Groups/invitations.html", invite_list=invite_list)

@group.route("/accept/<number>", methods=["GET"])
def accept(number):
    """
    Allows users to accept group invitations
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    record = (True, number, session["id"])
    query("""UPDATE memberlist
            SET Accepted=%s
            WHERE GroupID=%s AND UserID=%s""", record)

    flash("Joined group successfully")
    return redirect(url_for("group.groups"))

group.route("/decline/<number>", methods=["GET"])
def decline(number):
    """
    Allows users to decline group invitations
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    record = (number, session["id"])
    query("""DELETE FROM memberlist
            WHERE GroupID=%s AND UserID=%s""", record)

    flash("Group declined successfully")
    return redirect(url_for("group.groups"))


@group.route("/new_group/", methods=["POST", "GET"])
def new_groups():
    """
    Allows users to create new groups
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    message = ""
    if request.method == "POST":
        name = request.form["Name"]
        description = request.form["Description"]

        record = (name,)
        select_group = query("""SELECT GroupName FROM groups WHERE GroupName = %s""", record)
        try:
            name_check = not empty(select_group)
            
        except:
            name_check = True

        try:
            captcha = request.form['captcha']
            captcha = True
        except:
            captcha = False
        
        if not(captcha):
            message += "Invalid captcha<br>"
        if(empty(name) or empty(description)):
            message += "Please fill in all fields<br>"
        if (len(name)>20):
            message += "Name is too long<br>"
        if(name_check):
            message += "This group name is already taken<br>"
        if(len(description)>256):
            message += "The description is too long, max 256 characters<br>"

        if(empty(message)):
            owner = session["id"]

            record = (name, description, owner)
            query("""
                INSERT INTO
                groups (GroupName, GroupDescription, Owner)
                VALUES
                (%s, %s, %s);
                """,
                record)

            select_group = query("""SELECT GroupID FROM groups WHERE 
                                GroupName = %s AND GroupDescription = %s AND Owner = %s""", 
                                record)
            
            record = (select_group[0][0],owner, True)
            query("""
                INSERT INTO
                memberlist (GroupID, UserID, Accepted)
                VALUES (%s, %s, %s);
                """,
                record)

            flash("Group created successfully")
            return redirect(url_for("group.groups"))

    return render_template("Groups/new_group.html", message=message, showMessage = not empty(message))

@group.route("/members/<number>", methods=["POST", "GET"])
def group_members(number):
    """
    Allows members to view a list of all group members
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    if not group_check(number, session["id"]):
        return redirect(url_for("group.groups"))

    user = session["id"]
    record = (number,)
    select_group = query("""SELECT GroupName, Owner, Username
                            FROM groups INNER JOIN user 
                            ON groups.Owner = user.UserID
                            WHERE GroupID = %s""", record)
    select_member = query("""SELECT Username, Email, Accepted, user.UserID
                            FROM memberlist INNER JOIN user
                            ON memberlist.UserID = user.UserID
                            WHERE GroupID = %s
                            ORDER BY Accepted DESC""", record)

    group_name = select_group[0][0]
    owner = select_group[0][1]
    owner_name = select_group[0][2]
    
    return render_template("Projects/members.html", members = select_member , user_id = user, 
                            group_name = group_name, owner = owner, owner_name = owner_name , group_id = number)