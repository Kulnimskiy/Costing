# COSTING
#### Video Demo:  <URL HERE>
#### Description:
COSTING is a platform to spy on your competitors and keep track of their prices on the same commodities that you sell.
First the user goes through the authentication process. The routes responsible for the authentication are located in 
the auth.py file. There you are able to sign up, log in, and log out.


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
   avoid writing the same web scraper multiple times for each company. It also helps
   **project/search_files/async_search.py** find the needed scraper faster with less overload for the server
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















source to get the select with filter https://www.youtube.com/watch?v=qNO37iMzmFY


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
- filters by the color of the price on the comparison page
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
