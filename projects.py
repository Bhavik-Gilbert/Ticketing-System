from flask import Blueprint, redirect, url_for, render_template, request, session, flash

project = Blueprint("project", __name__, static_folder="static", template_folder="template")

from functions import logged_out, owner_check, group_check, empty, project_check

from connection import query

@project.route("/<number>", methods=["POST", "GET"])
def projects(number):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    if not group_check(number, session["id"]):
        return redirect(url_for("group.groups"))

    record = (number,)
    select_group = query("""SELECT GroupID, GroupName, GroupDescription, Owner
                            FROM groups
                            WHERE GroupID = %s""", record)
    
    record = (number,)
    select_projects = query("""SELECT Name, ProjectDescription, user.Name, projectlist.UserID, Manager, projects.ProjectID
                            FROM projects INNER JOIN user ON 
                            projects.Manager = user.UserID
                            INNER JOIN projectlist ON
                            projects.ProjectID = projectlist.ProjectID
                            WHERE projects.GroupID = %s""", record)
    
    user = session["id"]
    projects_in = []
    projects_out = []
    for project in select_projects:
        if(project[3] == user):
            projects_in.append(project)
        else:
            projects_out.append(project)

    return render_template("Projects/projects.html", group_id = select_group[0][0], group_name = select_group[0][1], group_description = select_group[0][2], owner = select_group[0][3],
                            projects_out = projects_out, projects_in = projects_in, user = session["id"])

@project.route("/<number>/new_project", methods=["POST", "GET"])
def new_project(number):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    if not group_check(number, session["id"]):
        return redirect(url_for("group.groups"))

    message = ""
    if request.method == "POST":
        name = request.form["Name"]
        description = request.form["Description"]

        record = (name,)
        select_project = query("""SELECT ProjectName FROM projects WHERE ProjectName = %s""", record)

        try:
            name_check = not empty(select_project)
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
            message += "This project name is already taken<br>"
        if(len(description)>256):
            message += "The description is too long, max 256 characters<br>"

        if(empty(message)):
            manager = session["id"]

            record = (name, number, description, manager)
            query("""
                INSERT INTO projects (ProjectName, GroupID, ProjectDescription, Manager)
                VALUES (%s, %s, %s, %s);""", record)

            select_group = query("""SELECT ProjectID FROM projects WHERE 
                                ProjectName = %s AND GroupID = %s AND ProjectDescription = %s AND Manager = %s""", 
                                record)
                                
            record = (select_group[0][0], manager)
            query("""
                INSERT INTO
                projectlist (ProjectID, UserID)
                VALUES (%s, %s);
                """,
                record)


            flash("Project created successfully")
            return redirect("/projects/" + number)
    
    record = (number,)
    select_project = query("""SELECT GroupName FROM groups WHERE GroupID = %s""", record)

    return render_template("Projects/new_project.html", message=message, showMessage = not empty(message), group_name=select_project[0][0])


@project.route("/<number>/delete_project/<number2>", methods=["POST", "GET"])
def delete_project(number,number2):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (number2,)
    select_manager = query("""SELECT Manager FROM projects
                            WHERE projects.ProjectID = %s""", record)

    if owner_check(select_manager[0][0],"Project deleted successfully","Only the manager can delete a project","Error deleting project"):
        record = (number2,)
        query(""" DELETE FROM tickets 
                WHERE ProjectID = %s""", record)

        query(""" DELETE FROM projectlist 
                WHERE ProjectID = %s""", record)
            
        query(""" DELETE FROM projects 
                WHERE ProjectID = %s""", record)

    return redirect("/projects/" + number)


@project.route("/<number>/remove_user/<number2>/<user>", methods=["POST", "GET"])
def remove_user(number,number2, user):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (number2,)
    select_manager = query("""SELECT Manager FROM projects
                            WHERE projects.ProjectID = %s""", record)

    if owner_check(select_manager[0][0],"User removed successfully","Only the manager can remove a user","Error removing user"):
        record = (number2, user)
        query(""" DELETE FROM projectlist
                WHERE ProjectID = %s AND UserID = %s""", record)

    return redirect("/projects/" + number)

@project.route("/<number>/leave_project/<number2>", methods=["POST", "GET"])
def leave_project(number,number2):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (number2,)
    select_manager = query("""SELECT Manager FROM projects
                            WHERE projects.ProjectID = %s""", record)

    if not owner_check(select_manager[0][0],"Managers cannot leave a project","Project left successfully","Error leaving project"):
        record = (number2,session["id"])

        query(""" DELETE FROM projectlist 
                WHERE ProjectID = %s AND UserID = %s""", record)
            
    return redirect("/projects/" + number)

@project.route("/<number>/join_project/<number2>", methods=["POST", "GET"])
def join_project(number,number2):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (number2,)
    select_manager = query("""SELECT UserID FROM projectlist
                            WHERE ProjectID = %s""", record)

    if empty(select_manager):
        record = (number2,session["id"])
        query("""INSERT INTO projectlist (ProjectID, UserID)
                VALUES (%s, %s);""", record)

        flash("Group joined successfully")
    else:
        flash("You are already in this group")
            
    return redirect("/projects/" + number)

@project.route("/members/<number>/<number2>", methods=["POST", "GET"])
def project_members(number,number2):
    if(logged_out()):
        return redirect(url_for("start.login"))
    
    if not project_check(number2, session["id"]):
        return redirect(url_for("group.groups"))

    user = session["id"]
    record = (number2,)
    select_project = query("""SELECT ProjectName, projects.Manager, user.Username
                            FROM projects INNER JOIN user
                            ON projects.Manager = user.UserID
                            WHERE ProjectID = %s""", record)

    select_member = query("""SELECT Username, Email, user.UserID
                            FROM projectlist INNER JOIN user
                            ON projectlist.UserID = user.UserID
                            WHERE ProjectID = %s""", record)

    project_name = select_project[0][0]
    manager = select_project[0][1]
    manager_name = select_project[0][2]
    
    return render_template("Tickets/members.html", members = select_member , user_id = user, group_id = number,
                            project_name = project_name, manager = manager, manager_name=manager_name, project_id = number2)