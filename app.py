''' This file is the application file serving the python logic for 
different routes and templates used by the web app'''

import os
import urllib.request

from flask import Flask, render_template, request
from flask_session import Session

from helpers import (
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
    drivers_all_years,
    team_standings_year,
    driver_standings_year,
)

from seasons import (
    season_list,
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
# dict of seasons + race_name - not used anymore but kept to prompt line 234
SEASONS_AND_NAMES = False
# dict for storing seasons, race_names + rounds for javascript options on results post
# hard coded up to end of 2024 season and API used to pull and append data 2025 on
seasons_and_races = season_list


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
        "drivers.html",
        driver_standing=driver_standing,
        CURRENT_SEASON=CURRENT_SEASON
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
            drivers_and_teams[team] = []
            for driver in drivers_for_team(team):
                d = driver["driver"]["driverId"]
                drivers_and_teams[team].append(d)

    team_standing = team_standings()["constructors_championship"]

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

    global SEASONS_AND_NAMES
    if SEASONS_AND_NAMES is False:
        # get list of all seasons available in API (need offset?)
        all_seasons = seasons_history()
        # to get new years / rounds and add them to the season key in the seasons_and_races dict
        for x in all_seasons:
            if x["year"] not in seasons_and_races:  # if year not already in dict (2025 onwards)
                seasons_and_races[x["year"]] = {}  # add that year key to dictionary
                year_races = races(x["year"])  # call API to pull all races for that year
                for r in year_races["races"]:  # for each race in that year
                    # add racename and round
                    seasons_and_races[int(year_races["season"])].update({r["raceName"]: r["round"]})
        SEASONS_AND_NAMES = True

    # for dict of all drivers in all years
    all_drivers_dict = {}
    if not all_drivers_dict:
        all_drivers = drivers_all_years()
        for driver in all_drivers:
            all_drivers_dict[driver["driverId"]] = driver

    if request.method == "POST":
        year = request.form.get("season")
        racename = request.form.get("racename")

        # Below is to avoid issue of where rounds are set as 'None' at start of year
        try:
            race_round = seasons_and_races[int(year)][racename]
        except (ValueError, KeyError, IndexError):
            link = "/results"
            message = "Data not available"
            return render_template("error_message.html", message=message, link=link)

        # if no constructor or driver entered on submit or doesnt exist
        if not year:
            link = "/results"
            message = "Please select a year in the dropdown"
            return render_template("error_message.html", message=message, link=link)
        if not race_round:
            link = "/results"
            message = "Please select a round in the dropdown"
            return render_template("error_message.html", message=message, link=link)

        try:
            qualify = qualifying(year, race_round)  # for getting qualy data for selected race
            qualify_data = qualify["races"]
        except (ValueError, KeyError, IndexError):
            qualify = None
            qualify_data = None

        try:
            selected_data = result(year, race_round)  # for getting result data for selected race
            result_data = selected_data["races"]
            if not os.path.isfile(
                f'./static/race_pics/{selected_data["races"]["raceName"]}.jpg',
            ):
                wiki_url = selected_data["races"]["url"] # to pull pic for race loaded on page
                wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
                url = picture(wiki_search_title) # uses title for API search to pull picture
                if url:
                    urllib.request.urlretrieve(
                        url,
                        f'./static/race_pics/{selected_data["races"]["raceName"]}.jpg',
                    )
        except (ValueError, KeyError, IndexError):
            result_data = None

        try:
            fastest_lap = fastest(year, race_round)  # for getting fastest lap of selected race
            # to check if dict contains any None values which would break results HTML
            if fastest_lap["fast_lap_driver_id"] is None:
                #set entire dict to None so logic in results.html can skip
                fastest_lap = None
        except (ValueError, KeyError, IndexError):
            fastest_lap = None

        return render_template(
            "results.html",
            year = year,
            racename = racename,
            race_round = race_round,
            seasons_and_races=seasons_and_races,
            fastest_lap=fastest_lap,
            data=selected_data,
            result_data=result_data,
            qualify=qualify,
            qualify_data=qualify_data,
            all_drivers_dict=all_drivers_dict,
        )

    # if not post but get method
    else:
        # below checks to see if season hasnt been built yet and adds a hardcoded default to show
        try:
            data = result_default()
            result_data = data["races"]
            if not os.path.isfile(
                f'./static/race_pics/{data["races"]["raceName"]}.jpg',
            ):
                wiki_url = data["races"]["url"] # to pull picture for specific race loaded on page
                wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
                url = picture(wiki_search_title) # uses title for API search to pull picture
                if url:
                    urllib.request.urlretrieve(
                        url,
                        f'./static/race_pics/{data["races"]["raceName"]}.jpg',
                    )
        except (ValueError, KeyError, IndexError):
            data = None
            result_data = None

        try:
            qualify = qualifying_default()
            qualify_data = qualify["races"]
        except (ValueError, KeyError, IndexError):
            qualify = None
            qualify_data = None

        try:
            fastest_lap = fastest(data["season"], data["races"]["round"]) # get fastest lap of race
            # to check if dict contains any None values which would break results HTML
            if fastest_lap["fast_lap_driver_id"] is None:
                #set entire dict to None so logic in results.html can skip
                fastest_lap = None
        except (ValueError, KeyError, IndexError):
            fastest_lap = None

        return render_template(
            "results.html",
            seasons_and_races=seasons_and_races,
            fastest_lap=fastest_lap,
            data=data,
            result_data=result_data,
            qualify_data=qualify_data,
            qualify=qualify,
            all_drivers_dict=all_drivers_dict,
        )


@app.route("/season_history", methods=["GET", "POST"])
def season_history():
    """allows user to pick season and list winning team and driver for that year"""

    # logic for looking up and seasons and creating dictionary
    all_seasons = seasons_history()
    seasons = {}  # initialises seasons dict for dropdown menu
    for x in all_seasons:
        seasons[x["year"]] = x["year"]


    if request.method == "POST":
        selected_season = request.form.get("season")
        # if no season entered on submit or doesnt exist
        if not selected_season:
            link = "/season_history"
            message = "Please select a season"
            return render_template("error_message.html", message=message, link=link)

        team_standing_year = team_standings_year(selected_season)
        driver_standing_year = driver_standings_year(selected_season)
        season_data = races(selected_season)

        return render_template(
            "season_history.html",
            season=selected_season,
            seasons=seasons,
            team_standing_year=team_standing_year,
            driver_standing_year=driver_standing_year,
            season_data=season_data,
        )

    # if method = GET
    else:

        season_data = previous_race()

        global CURRENT_SEASON
        if not CURRENT_SEASON:
            CURRENT_SEASON = season_data["season"]

        team_standing_year = team_standings_year(CURRENT_SEASON)
        driver_standing_year = driver_standings_year(CURRENT_SEASON)

        return render_template(
            "season_history.html",
            season=CURRENT_SEASON,
            seasons=seasons,
            team_standing_year=team_standing_year,
            driver_standing_year=driver_standing_year,
            season_data=season_data,
        )
