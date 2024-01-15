
CHECK HOW TO ADD NEW MODELS TO AN EXISTING DB

Search page:
- need parsers for an item's page and a search page of the main competitors of stomart
- 




to do:
- create a button "request prices connection" next to a competitor

initial tasks for the profile page:
- save the data in a new table "companies" with the corresponding keys. Foreign key is inn!
- - create a model (Done)
- - remake all the instances (Done)
- - create a function to save the data (Done)
- if the data in the table hasn't been refreshed for a set period of time or if there are no data, reload them. (Done)
- if the field in HIS profile is empty, let the user add the info oneself or change it.
- If he wants to add the info about his competitors, he can change only fields with NONE in it
- you need a simple profile to see that the info about the logged user is correctly shown (Done)
- load up additional info about the user using a web scraper (Done)


THE BEGINNING OF THE MAIN PART

ENOUGH FOR THE AUTHENTICATION PART 
to do:
- finish up the registration pages front end (Done)
- js script to check the password as the user types it and say if it is valid and visualize it (Done)
- ajax script to check if the current login and inn is available (Done)

login requirements: (Done)
- len >= 3
- unique

to do:
- login checker function (returns false if the login satisfies the requirements else return login) (Done)
- email validation funk (Done)


password requirements: (Done)
- len >=6
- has uppercase letters 
- has alpha
- no spaces
- has digits 
- has lowercase letters

to do (Done):
- password checker function (Done)

I did not start writing this from the very beginning!

useful links
https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
to create the tables in db
from project import create_app, db                                
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()

