
Last possible features:
Necessary 
- make it so that on the profile there was the correct number of goods, competitors (DONE)
- add connection though the price looker
- add item through the price looker
- show names of the items in the profile, Not links
- autoload associations (takes every user's item and looks for it on every competitor's site getting  items with a
set similarity wiggle room) Need to get the needed similarity from the Competitors and items file
- add connection to existing items using a dropdown or input autocomplete field in tracked goods
- filters by the color of the price on the comparison page
- refine the code
- refine the view of the pages
- clear the db and test

Preferred
- filters by competitor
- load items (using an Excel spreadsheet with 3 columns (name, price, link)) and add a button to get a template excel






Make profile and web links vital to work with


Profile (DONE)
 - html for request to connect your site to return
   - displays: input link to request connection to the clients website
   - displays: request connection button
   - or add items manually
   - 
 - 



!remake the scraper tamplate
! remove the ItemsConnection model and tables

create new models !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Search page:
- need parsers for an item's page and a search page of the main competitors of stomart (done)
- work out how to give the user only HIS parsers
It could be implementer like this:
- as the person registers, a folder with his loging as a name is created
- when the client adds a competitor a file with a competitors inn as a name is created and
- it adds the path to the parser to a table (cl
- ient_scrapers(col (number, inn, path)))
- NEED TO ADD A COLUMN TO THE COMPETITORS TABLE(STATUS(CONNECTED\NOT CONNECTED(OR TRUE\FALSE)))
- search looks for all the scrapers of the connected competitors by their inn, finds their paths and imports the classes
into a file "search all" where the search happens asynchronously through all the websites
- if the scraper is already somewhere. it connects when the admin changes the status of the connection
from "disconnected" to "connected". When it's connected the paths for all the connected ones is gotten 
from the Model Scrapers




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

