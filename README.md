# CS50 Project - Formula One Season tracker
#### Video Demo:  <https://youtu.be/d_uCtAK45fU>
## Overview
    This project looks to create a convenient way to show info for the current formula one season, including drivers & teams standings, as well as results. It makes use of a Formula One API (Ergast - http://ergast.com/mrd/) to get data, a Wikimedia API for grabbing images of drivers, tracks etc, and also a Bing maps API to display race locations.

    The means by which I've chosen to implement this project is through a web-based application using Python (Flask), Jinja, HTML, CSS, JavaScript and SQL. SQL was used initially to set up the database for users (project.db database containing the users table as well as the initial setup code in table_creation.sql). This database is then used anytime a user tries to login, register or deregister their account. The bulk of the web app is coded in python (in app.py) and uses multiple functions, including functions for calling APIs (in helpers.py). I chose to utlise Flask as a web framework for displaying pages and the data within. Flask uses HTML templates (set up from a 'parent' layout file) to render the web pages. I've also used Bootstrap as a CSS framework to style my web pages for consistency, aestetics and ease. There is also a small amount of additional, more custom CSS in a CSS styles file.

    On loading, the app determines whether you are logged in and gives you options to log in or create an account. Once validated and passwords satisfied (or in the case of new people that your username doesn't already exist) you will be redirected to the home page. This loads information about upcoming races and pictures and map data for them.

    The drivers page in the Nav-bar displays data for the current drivers in the championship in order
    The teams page in the Nav-bar displays data for the current teams in the championship in order
    The race results page in the Nav-bar shows by default the most recent race data in a table, but also allows the user to search and select a historic race to display data for
    The driver history page in the Nav-bar lets you pick a current team and then driver to show the history of their career with that team, in a table displayed on the page.
    You can also log out from the nav-bar, link back to the home page multiple ways, or choose to manage account and deregister.

## Files & contents

### **Static**
    The static folder at the root of the project is for holding the folders for images returned from APi calls (for Driver, Race, Teams and Track pictures). This is in an aim to improve the efficiency of the app as these pictures can be pulled from here in the future rather than repeatadly doing API calls. There are then also a few image files for logos which are used in headers and footers on pages. Finally, the file styles.css holds the CSS for any custom CSS not being handled by Bootstrap. This is mainly for handling logos contained within certain bootstrap elements, as well as custom table styling and all the custom colour codes for the main and current Formula One teams.

### **Templates**
    The Templates folder holds all the flask template files to be interacted with and rendered, as well as for variables being passed through using placeholders and Jinja syntax.

    • deregister.html
    This file is to be rendered if a user wishes to deregister their account. It involves a submit button for deregistering, which then triggers a Bootstrap pop-up message for confirmation. Once confirmed it calls POST on the deregister route /deregister

    • driver_history.html
    This file starts with some JavaScript for the drop down lists on the page. They work by being passed the names dictionary which contains the list of teams and drivers. It then allows the first dropdown items to be populated from the team names as the dictionary keys and then once selected the second drodown will populate from the values (drivers) associated with that key (team)
    On submit (POST) it will render and pass back the driver's name and team and populate a table with information about all the seasons they've raced with that team.

    • drivers.html
    This template displays all the drivers in the current season, along with their information, in order of their position within the driver's championship. This is done utlising Flask to pass through a dictionary containing all the data, and then iterating through that and displaying data using Jinja syntax, onto Bootstrap cards.

    • error_message.html
    Is triggered by user input errors - displays page with custom content using placeholders, for variables passed via render_template based of what the issue is. For exampe if the user's login details are incorrect it will render a new page with a message telling them the issue, with then a link back to the previous page / page where they can correct the input.

    • index.html
    This is our home page and the first page you see once logged in. It uses bootstrap cards to show different race data based on the previous, next and then the race after that in the schedule.
    For each card it displays info about the race and uses the WIKIMEDIA API to pull a picture from the WIKIPEDIA page for that race. It then also grabs the coordinates for that race and displays it via Bing Maps API.
    There is also some conditional logic (if - else statements) to defensively program for season changes. For example if the schedule for next season isn't ready it won't display any results and be blank (as opposed to an internal server error).

    • layout.html
    The main layout.html file which contains the navbar / header for any HTML file rendered, as well as the footer (basically anything that is the same across pages). Contains the stylesheets for the pages as well as Boostrap plugins for CSS and JavaScript. Conditonal (if / else) for whether user is logged in. Renders different navbar based off this with links to log in / pages once logged in. Also passed in user name variable to display. Then show's the main block to be fed to other templates and finally a logo and reference / credit to the Ergast Formula 1 API being used by the webapp.

    • login.html
    Page with a form for entering your login information and SUBMIT

    • register.html
    Page for registering an account by providing name and password (and confirmation of password) with SUBMIT

    • results.html
    This file starts with some JavaScript for the drop down lists on the page. They work by being passed the seasons_and_rounds dictionary which contains the list of seasons and rounds within. It then allows the first dropdown items to be populated from the seaons as the dictionary keys and then once selected the second drodown will populate from the values (rounds) associated with that key (season)
    By default it will display the most recent race data, but on submit (POST) it will render and pass back the selected race's details in the tables below, including the picture for the track / race. There is also some conditional logic in this template to deal with races where certain drivers havn't set any personal fastest lap, or races where overall fastest lap wasn't recorded.
    There is also then some JavaScript which allows for the results table data above to be exported to csv and downloaded by the user

    • teams.html
    This template displays all the teams in the current season, along with their information, in order of their position within the constructor's championship. This is done utlising Flask to pass through a dictionary containing all the data, and then iterating through that and displaying data using Jinja syntax, onto Bootstrap cards.

### **app.py**
    This is perhaps our 'main' file doing most of the work of the webapp. It begins by importing the OS module and urllib.request module for their functionalities to be used later.
    It imports SQL module from cs50 for ease of interacting with and configuring my SQLite database.
    It then imports from flask various modules to allow for the main functionalities of my webapp (e.g redirects and templates being rendered).
    Some modules from werkzeug.security are imported for dealing with passwords (the hashing and checking of those hashed passwords for user accounts).
    Then all my helper functions and API functions are imported form my helpers.py file which will bse used within my app.
    It then configures my flask app and also configures it to store sessions locally as opposed to inside cookies.
    Still within the set up of the file at the top are my top level global variables (dictionaries etc). These are here to be written to as my app runs so they are only required to be created once and can be used across all routes and also reset when users log in and out. This limits the calling of API functions in creating these dictionaries and makes my webapp a lot more efficient (only slow when loading and running the first time for some pages).
    Routes are decorated with @login_required (which is defined in my helpers file) to ensure that users are logged in before accessing the main site.

    @app.context_processor - this is to create a dictionary of user session to make user available before templates are rendered

    @app.after_request - This is to ensure that responses are not cached - caching responses is the default for Flask but may mean changes are not picked up by browser

    @app.route("/", methods=["GET"]) - Show's main page including upcoming race info. Grabs username from database using sessions userid as well as data for the most recent race, next race and race after that, as well as current season (these use API functions defined in helpers.py). Then the OS and URLLIB libraries to determine if pictures for tracks already exist, and if not to grab an image with my track_pic function and save it to my workspace for use again in the future. The main page route then checks if the teams_dict is populated and if not goes about calling API functions and generating data for this dictionary. It isn't actually necesaary for this route, only to preload so wait time isn't too long once clicking on /drivers route when it's got additional APIs to call. This is saved to a global dictionary so can be called by other routes and save time later. Finally render_template is called and variables passed in for track data for upcoming / previous races as well as a few other things requited for the HTML template.

    @app.route("/drivers", methods=["GET"]) - Gets info for current drivers and displays their info in order of season standings. It does this by first chekcing if the teams_dict and drivers_dict are populated and if not goes about calling API functions to poulate these. It then uses these to populate another dictionary for matching drivers to teams (drivers_and_teams). Then similar to the tracks, we iterate through out driver dictionary to check if driver pictures already exists in our Static folder in our workspace and if not calls APIs and functions get these. Following this it calls our driver_standing function to do an API call so we can render the driver's in order of their place in the championship.

    @app.route("/teams", methods=["GET"]) - Gets info for current teams and displays their info in order of season standings. Similar to the driver route it does this by first chekcing if the teams_dict is populated and if not goes about calling API functions to poulate. We then check our global team_pics variable and if it's not already been run and set to True, we iterate through out teams dictionary to check if each team pictures already exists in our Static folder in our workspace and if not calls APIs and functions get these. It then set's the team_pic variabble to True. It then checks the drivers_dict is populated and if not goes about calling API functions to poulate. It then uses these dictionaries to populate another dictionary for matching drivers to teams (drivers_and_teams) if not already called in another route like /drivers. Finally it calls our team_standing function to do an API call so we can render the team's in order of their place in the championship before rendering the template and passing in the dictionaries and season etc.

    @app.route("/results", methods=["GET", "POST"]) - Show's results of current race and allows users to select historical races to view. Starts by initialising a dict for season and round combos and then a entire history of rounds from an API function. I then iterate through what is returned by the API to populate the dictionary keys and values separately. We then call a function for returning results of the latest race as a defualt value for the page (GET as opposed to the POST once the user interacts and submits which race they want data for). We then pull the url for the wikipedia page for that race and pass that URL into my picture function to return the main image from that wikipedia page and save it to my workspace (assuming data is returned). I set a few variable for the current round number and season and then I use a function for working out the overall fastest lap of that race and store it as a variable. I then trim down the data to just the data i need from here and store it in the result_data variable. Then if the user has interacting with thr page, submit and sent a POST request, then we look at the form on the page and pull the year and round. There's a bit of logic to confirm the user has correctly selected a valid year and round and displays an error page if not. With that satisfied though, we move on and run some functions for the overall fastsest lap and other data for that race. If data is present we will, similar to before, pull the wikipedia article picture (using the url from the returned API data) and save it for displaying. We then return redner template to display the user selected data, or if POST hasn;t been called we'll dipslay the GET default data.

    @app.route("/driver_history", methods=["GET", "POST"]) - allows user to pick drivers from current teams and list all the seasons that they've been with that team. Similarly to before checks for driver and team dictionaries in order to make sure they're present and if not populate them for use here and elsewhere. We then check for our names_dict and if not populated, we use the teams_dict to set the keys as the names of the teams (rather than the id of the team so it's more user focused for the form dropdowns). It then also iterates through the data from a function which takes the team and gives us the drivers for that team, which it addes as values (by name though not id so more user oriented). We then create two dictionaries which store the team names and ids and the drivers names and ids respectively in them as key / value pairs (for use later to match data to names on POST). If the request method is POST then we get the user's choice of team and driver from the form on the page (and check they are valid with similar logic as earlier - rendering error page if not). We then use the user's choices as arguments for out lookup API to return data for all the seasons that driver raced with that team. We then either render the POST template or if not we will have passed and render the GET template with blank values for some fields to avoid errors on the page trying to pull blank data.

    @app.route("/login", methods=["GET", "POST"]) - This route is for loggin users in. It starts by clearing any previous sessions and then also resetting global variables, so when the next user logs in it recalls the data etc to make sure it's up to date for this session. If the route is post it checks that the user has entered a username and password as well as querying that the user is in the user database. Once done it checks that that user's password matches what they have put (using HASH). If all good it set the session user id as that user and then continues to redirect to the homepage. If not and the request method is POST then it will render ythe login template as default.

    @app.route("/logout") - Somewhat similar to logging in, this starts by clearing the session and then proceeding to clear the global variables. We do both as a defensive way to make sure nothing is carried over between logging in and out. Then redirects user to homepage (which will then check login and redirect to login if needed)

    @app.route("/register", methods=["GET", "POST"]) - This route is for users wanting to register in order to be able to login and use the site. It starts by checking if POST method and if so retrieving from the form on the page the username password and confirmation submitted. There's some logic to ensure these have been entered (directing the user to an error page if not with the option to return to input values again), as well as if the username already exists,or if the user failed to confirm the password properly. If all checks passed then we create the new user by inserting our python variables (username password and hashed password using our werkzeug module) into our SQlite database and redirect the user to the main / home / index page. If the user has not submitted via POST then we skip all the above and it goes through the GET logic of rendering the register.html template for users to fill out.

    @app.route("/deregister", methods=["GET", "POST"]) - this route is for deleting user accounts essentially. If the user submits via POST then it deletes that user (going off their session userid)from the database and redirects them to the logout route (resetting all the global variables etc and allowing to login or register again) if no POST request we instead redner the deregister template for the user which will then require to user to make a final confirmation and submit it via POST to initiate the above.

### **helpers.py**
    This file contain all our functions - notably our API functions containing API calls and returning data.
    It begins by importing the python modules for requests (To allow us to make http requests to a web page using python) and urllib (for URL handling & retrieving). We then just import a few things from the Flask module we might need here, as well as the functools wraps Python module for decorating.

    def login_required(f): - this is our route decorator to require users to login for certain routes in app.py. Essentially, if there is no session user id (that is no one has logged in) it will redirect the person to the login page where they can register or login. This is required on the pages we don;t want non users having access to until they're created an account.

    def picture(wiki_search_title): -  MediaWiki API for returning main page image of an article - used in conjuction with URL received from ergast API.
    Here we first try to set a url variable using our predefined url and adding in our wiki_search_title argument for that wiki page. We also include some headers so that we are recognised by the API so they don't reject / limit our requests etc. We then try and save this request as our response variable. If it runs without error we'll let the user know and then save the returned thumbnail source as our data variable and return it. If it fails we will return None.

    def track_pic(track): - function for getting track pictures using the picture function defined above
    This function uses the above defined track_pic function and also uses the argument passed in for a wikipedia URL to use. We pass this argument for the URL into the picture function and then save what is returned to our workspace.

    def fastest(year, round): - API function for returning fastest driver in specified year and round
    we specify two arguments for year and round and enter them into our API call and try to pull a repsonse (returning data if successfull)

    def seasons_history(): - API function for returning seasons available in API
    This is an API call that pulls all the possible years and rounds from the API. However we have had to place an offset into the request as initally it was causing issues pulling that much data. I opted to prgogram defensively and limit the response and offset so rather than starting from the earliest ever recorded race, our list runs from the 1975 season. This also means that it will be quite a few years until we need to worry about the amount of data being pulled causing problems as time goes on and the dataset increases. It just means we can't pull data from the earlier seasons (thought the data is patchy and limited anyway the further back you go) If data then it returns, otherwise returns none.

    def result_default(): - API function for returning results of latest race
    Here we are just calling the API to return the most recent race result - something which is a predefined url by the API - we don't need to add any parameters. We return data if successful.

    def result(year, round): - API function for returning results from a specific race by season and round
    We have extra arguments for this function to allow us to run API calls using a specific round and year. This allows us to let the user pick a specific historical race they want data about 9used in the results route.

    def previous_race(): - API function for returning previous race before the most recent
    This uses similar logic as the call for pulling the latest race result data, but then goes further to get the current round number and calculate what the previous round would have been. It then uses this to pull data for that race (used in the index pages upcoming races cards layout to show previous and upcoming races.) There is also some logic for working out if it is the start of a new season and if so it can pull the last race of the previous season.

    def next_race(number): - API function for returning nth next race from the last (increments e.g 1 is next, 2 is the second race from now etc). We do this by passing in an argument which we use to add onto the current round for the API to return data about. Starts by calling API and deducing current round, then adds number argument to this and returns data for that round. There is some logic to determine if season end so app just laves blank rather than erroring.

    def teams_lookup(): - API function for returning all teams in current season
    Ergast API allows for this using 'current' in URL call and returns data for all teams in current sesason. Similar to other APi functions, checks for successful response and returns.

    def drivers_lookup(): - API function for returning all drivers in current season
    Ergast API allows for this using 'current' in URL call and returns data for all drivers in current sesason. Similar to other APi functions, checks for successful response and returns.

    def drivers_for_team(constructor): - API function for returning the drivers for a specific team
    We can utilise the API by declaring which teams we are intersted in and returning the list of drviers for that specific team. For this function we have an argument, which is our team / constructor name and this is used in the API URL to return to us the current drivers for that team.

    def driver_standings(): - API function for returning the drivers based on championship standing
    The Ergast API also allows us to simply call the current drivers and report back their standings in the championship. Returns none if any issues with the call.

    def team_standings(): - API function for returning the teams based on championship standing
    Similar to above, we can just call the API to request teams in order of their standing. If any issues with the response, return None.

    def lookup(driver, constructor): - API lookup for returning the different seasons a certain driver has been with a certain team. This is used by our driver_history route. It requires args for driver and team and then uses these in the API call to return data on the history of that driver with that team.

### **project.db**
    This is our SQLite database for storing all the user data. It is interacted with by app.py in order to add and remove user accounts as required.

### **README.md**
    This is the file you are reading right now, which contains a write up of the project. Here we aim to explain the project as well as giving an overview and description of what each of the files do and how it all works together. I also hope to explain why i made certain design choices and why I implemented things the way I have.

### **table_creation.sql**
    This is just the original SQL statement for creating our user table. Makes sure we have a unique key for our userids as well as username and password hash columns. The cash column is unused as the project changed scope slighty after the table was created. Decided adding funds and trying to do a fantasy sort of game within the F1 app was too broad / clutered and a differnt kind of app to the one i wanted to build.