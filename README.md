# COSTING
#### Video Demo:  <URL HERE>
#### Description:
COSTING is a platform to spy on your competitors and keep track of their prices on the same commodities that you sell.
First the user goes through the authentication process. The routes responsible for the authentication are located in 
the auth.py file. There you are able to sign up, log in, and log out.

## Story of oпшеrigin

I thought it'd be useful for some guys who sell dental equipment


## Project Design

Pic of a project design 

## Project Structure 

Here will be a project schema


### flask_session/

Contains users' sessions.

### instance/

Contains the database

To create all the tables in the database provided by the **project/module.py**, run the following command in your terminal:

```
python

from project import create_app, db 
                               
app = create_app()
with app.app_context():
   db.create_all()
```

The database file **db.sqlite3** contains 7 necessary tables:
1. users: 
   - *This model is used to store basic user information such as 
   company name, company INN, login, email, and password. It has been decided to identify users
   by their company inn as it's a unique identification number and cannot be repeated twice in the db.*
 
2. companies_info:
   - *This model stores information about companies, including their INN, website, organization, OGRN, 
   registration date, sphere, address, number of workers, CEO, and information loading date.*

   - *However, this info is gotten from another web source <https://checko.ru/>. 
   Costing uses a scraper to get the info by the company inn
   provided by the user. The code for the scraper in written in **project/search_files/search_company.py**.*

   - *The information is used to display on the main user page as he logs in and gets updated every 3 days*

3. competitors: 
   - *This model stores information about a user's competitors, including their connection statuses 
   (disconnected, connected, requested), competitor INN as a unique identifier, nickname, and website.*

4. scrapers: 
   - *This model stores paths to the companies' website scrapers to 
   avoid writing the same web scraper multiple times for each company and helping follow the DRY principle. 
   It also helps **project/search_files/async_search.py** find the needed scraper faster with less overload for the server
   when the db gets moved to a different one.*
 
5. usersitems: 
   - *This model stores unique connections between users and their items they want to keep track of.
   It could be their own items, or items from their competitors website (of course the competitors website needs
   to be connected aka the scraper has to be written and the competitor status needs to be changed to "connected"* 
   - *A user gets connected to an item via the item's link on the competitors website and the user's id*
   
 
6. itemsrecords: 
   - *This model stores all the records of items' prices, including the item name, company INN the item belongs to,
   price, date of the record, and link from the company's website.* 
 
7. itemsconnections: 
   - This model stores connections between items even when an item is deleted
   to support future features or item restoration by the user. When the connection has been added, one item's link
   gets associated with the other and the user can compare their prices

 

### project/

The main module that contains the working part of the app. There are 2 stages: authentication and main functionality


#### ./clients_scrapers/

This folder contains scrapers for competitors' websites. When a user registers, a folder is created with their inn as 
the name to avoid repetitions. The purpose of the folder is to store new scrapers for the user's competitors' 
websites if it hasn't been created yet. Additionally, if a user wants to connect their own website to the 
platform, a scraper template is created for their inn.  
 
When a user requests a competitor's connection, an email with all the necessary information is sent to the responsible admin (in this case, always me). The files responsible for writing a scraper template are as follows: 
1. text_templates/class_template.txt - a text version of a class to write a new scraper 
2. systems.py - stores classes containing the logic of creating, writing, and deleting scrapers 
3. server.py - main file with all the routes and manages server responses to user actions 
4. text_templates/request_connect_template.txt - a template of a request email 
5. emails.py - fills in the gaps in the request email text and sends it to the responsible admin 
6. credentials.py - stores credentials to the corporate email address (an env file was not created as the data needed to be accessed and changed across multiple devices over time. This data is not highly sensitive). 
 
If a user wants to delete a scraper, it will only be deleted if it has never been changed, as other users may also 
be using it. A competitor will only be connected to a user when the admin finishes implementing the scraper and 
changes the status of the competitor to "connected". This methodology could be improved by creating an admin panel 
and implementing version control.


#### ./search_files/

On our platform user can look for the needed item on multiple sites at the same time. This module helps connect all
the competitors scrapers our user has connected to his account and asynchronously work with them. 

Libraries such as *asyncio* and *aiohttp* make a perfect duo in saving time searching here. 
While the server waits the response from a competitors website, which sometimes takes a couple of seconds, instead of waiting 
for no reason, server sends a request to the next website etc.

- async_search.py - main search functionality
- get_classes.py has the functions to find the right scrapers files and import scraper class into the async_search.py file
- search_company - contains a Company class that helps find info about a company by its inn. Return value is a dict with the following info:
   - inn
   - website
   - organization
   - ogrn
   - registration_date
   - sphere
   - address
   - workers_number
   - ceo

### ./static/
Stores all the images, js files and everything else that is needed to bring the user experience to the next level
Each js file has a page to be working on. For homepage.js it is the "/" route. For the profile.js it is the "/profile"
route etc.

Mostly what js file do is sending ajax requests to the server when needed and updating information for a user.
For example, "homepage.js" allows a user to change his website information if it's not connected yet or change the email
reports will be sent to. However, if anyone tries to change their website when it's been connected,
the server will never allow it. All the constraints have been written in parallel to the frontend part.

### ./templates
Stores all the jinja html templates, that are used by the main routes to display information. 
the route "/price-looker" has 3 templates
"./price-looker.html" is needed to show the user the prices of all compatitors for the same
item when he tries to do so from the header.
The "./price-looker-results.html" is used inside the "./price-looker_layout.html" to get the user new results
sending the jinja template with the said results as a response to an ajax request. The request
itself is sent by the "price_looker.js"

### ./text_templates
The contents are:
- class_template.txt - used to write unfinished scrapers to a new file when website connection gets requested
- request_connect_template.txt - is a template for a message that gets sent to Admin when a request connection gets sent

The rest is two main files
auth.py - is the file responsible for the user authentication process
The routes in the file speak for themselves
- "/signup"
- "/login"
- "/logout"
- "/checklogin/<cur_login>" - checks if the login is already occupied by somebody else and cannot be taken
- "/checkinn/<cur_inn>" - checks if the company has already registered and send a response back to the fronted about the results

and server.py - where the main functional routes are stored. None of them can be accessed by a user if he is not loggged in.
Here is the list of all the routes implemented in this project:
- "/"
- "/profile"
- "/profile/load_item"
- "/company-goods"
- "/company-goods/refresh_all"
- "/company-goods/delete-item"
- "/competitor-monitoring"
- "/comparison"
- "/price-looker"
- "/profile/delete_competitor/<com_inn>"
- "/request_connection/<cp_inn>"
- "/profile/change_web"
- "/profile/change_email"
- "/profile/link_items"
- "/items_owned"
- "/autoload_associations"

#- Notes to myself (workflow)

Last possible features:

Necessary 
- make it so that on the profile there was the correct number of goods, competitors (DONE)
- add connection though the price looker (DONE)
- - chosen user's item input field (DONE)
- - if the item is chosen, add an item and add connection to the item (DONE)
- - if the item is empty, the item just gets added to the tracked item's list (DONE)
- show names of the items in the profile, Not links (DONE)
- autoload associations (takes every user's item and looks for it on every competitor's site getting  items with a
set similarity wiggle room) Need to get the needed similarity from the Competitors and items file (DONE)
- filters by the color of the price on the comparison page (DONE)
- refine the code
- refine the view of the pages
- clear the db and test

Preferred
- add connection to existing items using a dropdown or input autocomplete field in tracked goods
- filters by competitor
- load items (using an Excel spreadsheet with 3 columns (name, price, link)) and add a button to get a template excel



Make profile and web links vital to work with


Profile (DONE)
 - html for request to connect your site to return
   - displays: input link to request connection to the clients website
   - displays: request connection button
   - or add items manually
   -


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
source to get the select with filter https://www.youtube.com/watch?v=qNO37iMzmFY