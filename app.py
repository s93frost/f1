''' This file is the application file serving the python logic for 
differnt routes and templates used by the web app'''

import os
import urllib.request

from flask import Flask, render_template, request
from flask_session import Session

from helpers import (
    lookup,
    drivers_lookup,
    teams_lookup,
    drivers_for_team,
    driver_standings,
    team_standings,
    next_race,
    previous_race,
    result,
    result_default,
    fastest,
    seasons_history,
    picture,
    track_pic,
    qualifying,
    qualifying_default,
    races,
)

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# global variables - dictionaries etc - reset at login &
drivers_and_teams = {}
drivers_dict = {}
teams_dict = {}
names_dict = {}
TEAM_PICS = False
CURRENT_SEASON = ""
seasons_and_names = {}  # dict for storing seasons and race_name combinations
seasons_and_races = {}  # dict for storing seasons and race_name combinations


@app.after_request
def after_request(response):
    """This is to ensure that responses are not cached - caching responses
    is the default for Flask but may mean changes are not picked up by browser"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def index():
    """Show's main page including upcoming race info"""

    last_race = previous_race()  # variable for the most recent completed race

    #idented the below to check for last_race being built
    if last_race:
        global CURRENT_SEASON
        CURRENT_SEASON = last_race["season"]
    next_r = next_race(1)
    next_plus_one = next_race(2)

    # calling wiki picture api functions for each track if not already exists
    # checks if there is a last race returned by the API
    if last_race is not None and last_race is not False:
        if not os.path.isfile(
            f'./static/track_pics/{last_race["race"][0]["circuit"]["circuitName"]}.jpg'
        ):
            track_pic(last_race)

    # checks if next race returned by the API (for end of season)
    if next_r is not None and next_r is not False:
        if not os.path.isfile(
            f'./static/track_pics/{next_r["race"][0]["circuit"]["circuitName"]}.jpg'
        ):
            track_pic(next_r)

    # checks if next plus one race returned by the API (for end of season)
    if next_plus_one is not None and next_plus_one is not False:
        if not os.path.isfile(
            f'./static/track_pics/{next_plus_one["race"][0]["circuit"]["circuitName"]}.jpg'
        ):
            track_pic(next_plus_one)


    # dict of teams in currrent year - preloads so wait time isn't  long on /drivers route
    if not teams_dict:
        global teams  # global can be used by render template once self and teams_dict already made
        teams = teams_lookup()
        for team in teams:
            name = team["teamId"]
            teams_dict[name] = team

    return render_template(
        "index.html",
        next_r=next_r,
        next_plus_one=next_plus_one,
        last_race=last_race,
    )


@app.route("/drivers", methods=["GET"])
def drivers():
    """Gets info for current drivers and displays their info in order of season standings"""

    # for dict of all teams in currrent year
    if not teams_dict:
        # global so can be used by render template once already created and teams_dict already made
        global teams
        teams = teams_lookup()
        for team in teams:
            name = team["teamId"]
            teams_dict[name] = team

    # for dict of all drivers in currrent year
    if not drivers_dict:
        # global so can be used by rendertemplate if already created and teams_dict made
        global drivers
        drivers = drivers_lookup()
        for driver in drivers:
            drivers_dict[driver["driverId"]] = driver

    # for dictionary of all teams and their drivers in current year
    if not drivers_and_teams:
        for team in teams_dict:
            team_name = team
            drivers_and_teams[team_name] = []
            for driver in drivers_for_team(team):
                d = driver["driver"]["driverId"]
                drivers_and_teams[team].append(d)

    # to pull all pictures for drivers from their wikipedia url if file not already exists
    for x in drivers_dict.values():
        if os.path.isfile(
            f'./static/driver_pics/{x["name"]}{x["surname"]}.jpg'
        ):
            continue
        else:
            wiki_url = x["url"]
            # splits out page title from wiki page for API search
            wiki_search_title = wiki_url.split("/")[-1]
            # uses title for API function search tp pull picture
            url = picture(wiki_search_title)
            # if API call returns data, retrieve the URL and save it to my workspace
            if url:
                urllib.request.urlretrieve(
                    url,
                    f'./static/driver_pics/{x["name"]}{x["surname"]}.jpg',
                )

    driver_standing = driver_standings()

    return render_template(
        "drivers.html", driver_standing=driver_standing, CURRENT_SEASON=CURRENT_SEASON
    )


@app.route("/teams", methods=["GET"])
def constructors():
    """Gets info for current teams and displays their info in order of season standings"""

    # for dict  of all teams in currrent year
    if not teams_dict:
        # specify global can be used by rendertemplate if already created and teams_dict made
        global teams
        teams = teams_lookup()
        for team in teams:
            name = team["teamId"]
            teams_dict[name] = team

    # to pull all pictures for teams from their wikipedia url if file not already exists
    global TEAM_PICS
    if TEAM_PICS is False:
        for x in teams_dict.values():
            if os.path.isfile(
                f'./static/team_pics/{x["teamId"]}.jpg'
            ):
                continue
            else:
                wiki_url = x["url"]
                # splits out page title from wiki page for API search
                wiki_search_title = wiki_url.split("/")[-1]
                # uses title for API function search tp pull picture
                url = picture(wiki_search_title)
                if url:
                    urllib.request.urlretrieve(
                        url,
                        f'./static/team_pics/{x["teamId"]}.jpg',
                    )
        # sets variable as true after loop run so doesn't check again if already pulled
        TEAM_PICS = True

    # for dict of all drivers in currrent year
    if not drivers_dict:
        # global so can be used by rendertemplate if already created and drivers_dict  made
        global drivers
        drivers = drivers_lookup()
        for driver in drivers:
            drivers_dict[driver["driverId"]] = driver

    # for dictionary of all teams and their drivers in current year
    if not drivers_and_teams:
        for team in teams_dict:
            team_name = team
            drivers_and_teams[team_name] = []
            for driver in drivers_for_team(team):
                d = driver["driver"]["driverId"]
                drivers_and_teams[team].append(d)

    team_standing = team_standings()

    return render_template(
        "teams.html",
        drivers_dict=drivers_dict,
        drivers_and_teams=drivers_and_teams,
        team_standing=team_standing,
        CURRENT_SEASON=CURRENT_SEASON,
    )


@app.route("/results", methods=["GET", "POST"])
def results():
    """Show's results of current race and allows users to select historical races to view"""

    if not seasons_and_names:
        all_seasons = seasons_history()
        # get list of all seasons being pulled by API (offset due to size so starts in later year)
        for x in all_seasons:
            # this will need deleting out when all seasons / races available!!!!!!!!!!!!!!!
            if x["year"] == 2024:
                # list for the javascript options on results post
                seasons_and_names[x["championshipId"]] = []
                # dict to match names to rounds
                seasons_and_races[x["championshipId"]] = {}
        # to get all the rounds and add them to the season key in the dict
        for x in all_seasons:
            # this will need deleting out when all seasons / races available!!!!!!!!!!!!!!!
            if x["year"] == 2024:
                season_races = races(str(x["year"]))
                for r in season_races["races"]:
                    seasons_and_names[r["championshipId"]].append(r["raceName"])
                    seasons_and_races[r["championshipId"]].update({r["raceName"]: r["round"]})

    if request.method == "POST":
        year = request.form.get("year")
        racename = request.form.get("racename")
        race_round = seasons_and_races[year][racename]

        # if no constructor or driver entered on submit or doesnt exist
        if not year:
            link = "/results"
            message = "Please select a year in the dropdown"
            return render_template("error_message.html", message=message, link=link)
        if not race_round:
            link = "/results"
            message = "Please select a round in the dropdown"
            return render_template("error_message.html", message=message, link=link)

        fastest_lap = fastest(year, race_round)  # for getting fastest lap of selected race
        selected_data = result(year, race_round)  # for getting result data for selected race
        qualify = qualifying(year, race_round)  # for getting qualy data for selected race

        if qualify["races"]:
            qualify_data = qualify["races"]["qualyResults"]

        else:
            qualify = None
            qualify_data = None

        if selected_data["Races"]:
            result_data = selected_data["races"]["results"]
            wiki_url = selected_data["races"]["url"] # to pull picture for race
            wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
            url = picture(wiki_search_title) # uses title for API function search tp pull picture
            if url:
                urllib.request.urlretrieve(
                    url,
                    f'./static/race_pics/{selected_data["races"]["raceName"]}.jpg',
                )

        else:
            # if no data from API
            result_data = None

        return render_template(
            "results.html",
            seasons_and_names=seasons_and_names,
            fastest_lap=fastest_lap,
            data=selected_data,
            result_data=result_data,
            qualify=qualify,
            qualify_data=qualify_data,
        )

    # if not post but get method
    else:
        data = result_default()

        wiki_url = data["races"]["url"] # to pull picture for specific race loaded on page
        wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
        url = picture(wiki_search_title) # uses title for API function search tp pull picture
        if url:
            urllib.request.urlretrieve(
                url,
                f'./static/race_pics/{data["races"]["raceName"]}.jpg',
            )

        current_year = data["season"]
        current_round = previous_race()["round"] # round not included in result default api call
        fastest_lap = fastest(current_year, current_round) # for getting fastest lap of last race
        result_data = data["races"]
        qualify = qualifying_default()
        qualify_data = qualify["races"]

        return render_template(
            "results.html",
            seasons_and_names=seasons_and_names,
            fastest_lap=fastest_lap,
            data=data,
            result_data=result_data,
            qualify_data=qualify_data,
            qualify=qualify,
        )


@app.route("/driver_history", methods=["GET", "POST"])
def driver_history():
    """allows user to pick drivers from current teams and 
    list all seasons that they've been with that team"""

    # for dict of all teams in current year
    if not teams_dict:
        # global so can be used by rendertemplate if already created and teams_dict made
        global teams
        teams = teams_lookup()
        for team in teams:
            name = team["teamId"]
            teams_dict[name] = team

    if not drivers_dict: # for dict of all drivers in currrent year
        # specifiy global can be used by rendertemplate if already created and drivers_dict made
        global drivers
        drivers = drivers_lookup()
        for driver in drivers:
            drivers_dict[driver["driverId"]] = driver

    # dict for proper names for select drop-down instead of driver ids and constructor_ids
    if not names_dict:
        for team in teams_dict.values():
            team_name = team["teamName"]
            names_dict[team_name] = []
            for driver in drivers_for_team(team["teamId"]):
                d = driver["name"] + " " + driver["surname"]
                names_dict[team_name].append(d)

    # dict to store vaues of driver ids and names
    driver_names = {}
    for driver in drivers_dict.values():
        drivername = driver["name"] + " " + driver["surname"]
        driver_names[drivername] = driver["driverId"]

    # dict to store vaues of driver ids and names
    team_names = {}
    for team in teams_dict.values():
        tname = team["name"]
        team_names[tname] = team["teamId"]

    if request.method == "POST":
        drivers_name = request.form.get("driver_name")
        constructor_name = request.form.get("constructor_name")
        # if no constructor or driver entered on submit or doesnt exist
        if not constructor_name:
            link = "/driver_history"
            message = "Please select a team name"
            return render_template("error_message.html", message=message, link=link)
        if not drivers_name:
            link = "/driver_history"
            message = "Please select a driver name"
            return render_template("error_message.html", message=message, link=link)

        # pulls corresponding driver_id for the name selected on form held in drivers_name variable
        driver_id = driver_names[drivers_name]
        # pulls constructor_id for the name selected on form in constructor_name variable
        constructor_id = team_names[constructor_name]
        # my driver and constructor info API function
        info = lookup(driver_id, constructor_id)
        seasons = info["MRData"]["SeasonTable"]["Seasons"]

        return render_template(
            "driver_history.html",
            names_dict=names_dict,
            drivers_name=drivers_name,
            seasons=seasons,
            constructor_name=constructor_name,
            CURRENT_SEASON=CURRENT_SEASON,
        )

    # if method = GET
    else:
        seasons = ""
        constructor_name = ""
        drivers_name = ""

        return render_template(
            "driver_history.html",
            names_dict=names_dict,
            drivers_name=drivers_name,
            seasons=seasons,
            constructor_name=constructor_name,
            CURRENT_SEASON=CURRENT_SEASON,
        )
