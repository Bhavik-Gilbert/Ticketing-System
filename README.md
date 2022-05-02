# [Ticketing-System](http://bhavikgilbert.pythonanywhere.com/)

![Lines of code](https://img.shields.io/tokei/lines/github/Bhavik-Gilbert/Ticketing-System)

## What Am I
This repo is the codebase for a mockup task ticketing system. What this means is that users are able to create groups for teams to be invited to, which can host multiple projects where team members can access the different tasks that have been shared onto the system. Any user can take on a task shared, but once taken, only they can mark that task as completed unless they drop the task, in which case another team member will be able to take on the task in there stead.

This system helps teams to determine what work is avaiable alongside who completed what jobs, thereby making traceback and understanding for managers and colleagues much easier since they can find who did what and contact them about any questions.


## Technologies
### Framworks/Languages
This application is built using the flask module in python alongside sql in mysli_connector.
### Hosting
The website is hosted on [pythonanywhere.com](https://www.pythonanywhere.com) and is currently available for anyone to use


## Usage
### Getting started
To get started, users are required to signup to the system, inputted a regex secured password, which is then hashed and salted. From there, users will immediately be able to login and continue onto the site.
### Groups
Groups in this application are defined as different companies or teams, that plan to work on a number of projects together. Any user is able to make a group, and once made, this user becomes the admin. All groups require an admin, and only the admin can delete the group. If an admin wants to leave a group, the admin must first pass the role onto another user.
Gruops are invite only, admins are able to search through a list of all users to send them an invite request, the invited user is then able to accept or decline a request.
### Projects
Projects can be made by anyone in a group, with the creator becoming the project manager. Similar to group admins, each project is required to have a porject manager. Anyone in the group where the project is hosted is free to join, thereby making it quick and easy for group members to join new projects within the group.
### Task
Tasks can be created by anyone in a project, with one person in the project allowed to take on the task at a given time. Once taken on, the user is able to complete or drop the project, to free it up for other project members. All project members can view the past and active tasks that need completing and who is adn has done what, allowing for quick flow of communication in the situation where a mistake or lack of understanding occurs. The date of creation and completion is recorded to check how long the task took to be completed.
