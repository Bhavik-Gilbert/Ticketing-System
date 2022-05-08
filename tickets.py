from select import select
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from datetime import date

tickets = Blueprint("tickets", __name__, static_folder="static", template_folder="template")

from functions import logged_out, group_check, empty, project_check

from connection import query

@tickets.route("/your_tickets/", methods=["POST", "GET"])
def tasks():
    """
    Displays the tickets of the user
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    record = (session["id"], False)
    select_tickets = query("""SELECT tickets.TicketName, tickets.TicketDescription, groups.GroupName, projects.ProjectName, 
                            groups.GroupID, projects.ProjectID, tickets.TicketID FROM tickets 
                            INNER JOIN projects ON tickets.ProjectID = projects.ProjectID
                            INNER JOIN groups ON projects.GroupID = groups.GroupID
                            WHERE tickets.UserID = %s AND tickets.Completed = %s""", record)
    
    record = (session["id"], True)
    completed_tickets = query("""SELECT tickets.TicketName, tickets.TicketDescription, groups.GroupName, projects.ProjectName, 
                            groups.GroupID, projects.ProjectID, tickets.TicketID FROM tickets 
                            INNER JOIN projects ON tickets.ProjectID = projects.ProjectID
                            INNER JOIN groups ON projects.GroupID = groups.GroupID
                            WHERE tickets.UserID = %s AND tickets.Completed = %s""", record)

    return render_template("Tickets/your_tickets.html", tickets = select_tickets, completed = completed_tickets)

@tickets.route("/<number>/<number2>/", methods=["POST", "GET"])
def ticket(number,number2):
    """
    Displays the ticket of the project
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    record = (number2, False)
    select_tickets = query("""SELECT TicketID, tickets.UserID, ProjectID, TicketDescription, TicketName FROM tickets
                            WHERE ProjectID = %s AND Completed = %s ORDER BY UserID""", record) 

    record = (number2, True)
    select_completed = query("""SELECT TicketID, UserID, ProjectID, TicketDescription, TicketName FROM tickets
                            WHERE ProjectID = %s AND Completed = %s""", record)
    
    record = (number2,)
    select_project = query("""SELECT ProjectName, ProjectDescription, Manager FROM projects
                            WHERE ProjectID = %s""", record)

    return render_template("Tickets/tickets.html", tickets=select_tickets, completed=select_completed, project_name=select_project[0][0], project_description=select_project[0][1], 
                            manager=select_project[0][2], user_id=session["id"], project_id=number2, group_id=number)

@tickets.route("/delete_ticket/<number>/<number2>/<number3>/", methods=["POST", "GET"])
def delete_ticket(number,number2,number3):
    """
    Deletes the ticket
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    record = (number3,)
    query(""" DELETE FROM tickets 
              WHERE TicketID = %s""", record)

    flash("Ticket deleted successfully")
    
    return redirect("/tickets/"+number+"/"+number2)

@tickets.route("/new_ticket/<number>/<number2>/", methods=["POST", "GET"])
def new_ticket(number,number2):
    """
    Creates a new ticket
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    message = ""
    if request.method == "POST":
        name = request.form["Name"]
        description = request.form["Description"]

        record = (name,)
        select_project = query("""SELECT TicketName FROM tickets WHERE TicketName = %s""", record)

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
            message += "This ticket name is already taken<br>"
        if(len(description)>1024):
            message += "The description is too long, max 256 characters<br>"

        if(empty(message)):
            manager = session["id"]

            record = (number2, description, name)
            query("""
                INSERT INTO tickets (ProjectID, TicketDescription, TicketName)
                VALUES (%s, %s, %s);""", record)

            flash("Ticket created successfully")
            return redirect("/tickets/" + number + "/" + number2)

    record = (number2,)
    select_project = query("""SELECT ProjectName FROM projects
                            WHERE ProjectID = %s""", record)

    return render_template("Tickets/new_ticket.html", project_id=number2, project_name=select_project[0][0], message=message, showMessage = not empty(message))

@tickets.route("/view_tickets/<number>/<number2>/<number3>", methods=["POST", "GET"])
def view_ticket(number,number2,number3):
    """
    Displays the ticket details
    """

    if(logged_out()):
        return redirect(url_for("start.login"))
    
    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))
    
    record = (number2,)
    manager = query("""SELECT Manager FROM projects 
                       WHERE ProjectID = %s""", record)
    manager = manager[0][0]

    record = (number3,)
    select_ticket = query("""SELECT tickets.TicketName, tickets.TicketDescription, tickets.Completed, tickets.DateCompleted, tickets.UserID FROM tickets 
                            WHERE tickets.ticketID = %s""", record)
    
    select_user = query("""SELECT user.Username From tickets
                            INNER JOIN user ON
                            tickets.UserID = user.UserID
                            WHERE tickets.ticketID = %s""", record)
    
    if not empty(select_user):
        taken_user = select_user[0][0]
        taken = True
    else:
        taken_user = False
        taken = False
    
    started = not select_ticket[0][4] == None
    
    return render_template("Tickets/view_ticket.html", ticket = select_ticket[0], group_id = number, project_id = number2, ticket_id = number3, 
                            taken_user = taken_user, started = started, taken = taken, user = session["id"], manager = manager)

@tickets.route("/complete/<number>/<number2>/<number3>/", methods=["POST", "GET"])
def complete_ticket(number,number2,number3):
    """
    Marks the ticket as complete
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    record = (number3,)
    select_ticket = query("""SELECT tickets.Completed FROM tickets
                             WHERE TicketID = %s""", record)

    if not(select_ticket[0][0]):
        record = (True, date.today().strftime("%Y/%m/%d"), session["id"], number3)
        query(""" UPDATE tickets 
                SET Completed = %s, DateCompleted = %s, UserID = %s
                WHERE TicketID = %s""", record)

        flash("Ticket Completed")
    else:
        flash("This ticket has already been completed")

    
    
    return redirect("/tickets/"+number+"/"+number2)

@tickets.route("/drop/<number>/<number2>/<number3>/", methods=["POST", "GET"])
def drop_ticket(number,number2,number3):
    """
    Allows users to drop a ticket
    """

    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    record = (number3, session["id"])
    select_ticket = query("""SELECT tickets.UserID FROM tickets
                             WHERE TicketID = %s AND UserID = %s""", record)

    if not(select_ticket[0][0] == None):
        record = (None, number3)
        query(""" UPDATE tickets 
                SET UserID = %s
                WHERE TicketID = %s""", record)

        flash("Ticket dropped")
    else:
        flash("You currently aren't doing this ticket")

    
    
    return redirect("/tickets/"+number+"/"+number2)

@tickets.route("/start/<number>/<number2>/<number3>/", methods=["POST", "GET"])
def start_ticket(number,number2,number3):
    """
    Allows users to start a ticket
    """
    
    if(logged_out()):
        return redirect(url_for("start.login"))

    if not(group_check(number, session["id"]) and project_check(number2, session["id"])):
        return redirect(url_for("group.groups"))

    record = (number3,)
    select_ticket = query("""SELECT tickets.UserID FROM tickets
                             WHERE TicketID = %s""", record)

    print(select_ticket)
    if (select_ticket[0][0] == None):
        record = (session["id"], number3)
        query(""" UPDATE tickets 
                SET UserID = %s
                WHERE TicketID = %s""", record)

        flash("Ticket started")
    else:
        flash("This ticket is currently preocuppied by someone else")

    
    
    return redirect("/tickets/"+number+"/"+number2)