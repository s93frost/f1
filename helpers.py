''' This file is storing all the function & API call functions for web app '''
import urllib
from functools import wraps
from flask import redirect, session
import requests


def login_required(f):
    """Decorate routes to require login.  
    https://flask.palletsprojects.com/en/2.3.x/patterns/viewdecorators/#view-decorators"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def picture(wiki_search_title):
    """MediaWiki API for returning main page image of an article - 
    used in conjuction with URL received from ergast API"""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=pageimages|pageterms&piprop=thumbnail&pithumbsize=600&titles={wiki_search_title}&redirects=&pilicense=any"
        headers = {
            "User-Agent": "SffBot/0.0 (https://github.com/code50/47425976.git; sfproject@cs50.org)"
        }
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(f"picture: there's a {response.status_code} error with your request")
        data = response.json()["query"]["pages"][0]["thumbnail"]["source"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"picture: there's a {response.status_code} error with your request")
        return None


def track_pic(track):
    """function for getting track pictures using the picture function defined above"""
    wiki_url = track['race'][0]['url']
    # splits out page title from wiki page for API search
    wiki_search_title = wiki_url.split("/")[-1]
    # uses title for API function search tp pull picture
    url = picture(wiki_search_title)
    if url:
        urllib.request.urlretrieve(
            url,
            f'./static/track_pics/{track["race"][0]["circuit"]["circuitName"]}.jpg',
        )


def fastest(year, race):
    """API function for returning fastest driver in specified year and race"""
    try:
        response = requests.get(
            f"http://ergast.com/api/f1/{year}/{race}/fastest/1/results.json?limit=500", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(f"fastest: there's a {response.status_code} error with your request")
        data = response.json()["MRData"]["RaceTable"]["Races"][0]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"fastest: there's a {response.status_code} error with your request")
        return None


def seasons_history():
    """API function for returning seasons available in API"""
    try:
        response = requests.get("http://ergast.com/api/f1.json?limit=1000&offset=250", timeout=120)
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"seasons_history: there's a {response.status_code} error with your request"
            )
        data = response.json()["MRData"]["RaceTable"]["Races"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"seasons_history: there's a {response.status_code} error with your request"
        )
        return None


def result_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "http://ergast.com/api/f1/current/last/results.json?limit=500", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"result_default: there's a {response.status_code} error with your request"
            )
        data = response.json()["MRData"]["RaceTable"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"result_default: there's a {response.status_code} error with your request"
        )
        return None


def result(year, race):
    """API function for returning results from a specific race by season and race"""
    try:
        response = requests.get(
            f"http://ergast.com/api/f1/{year}/{race}/results.json?limit=500", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(f"result: there's a {response.status_code} error with your request")
        data = response.json()["MRData"]["RaceTable"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"result: there's a {response.status_code} error with your request")
        return None


def qualifying(year, race):
    """API function for returning results from a specific race by season and race"""
    try:
        response = requests.get(
            f"http://ergast.com/api/f1/{year}/{race}/qualifying.json?limit=500", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(f"result: there's a {response.status_code} error with your request")
        data = response.json()["MRData"]["RaceTable"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"result: there's a {response.status_code} error with your request")
        return None


def qualifying_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "http://ergast.com/api/f1/current/last/qualifying.json?limit=500", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"result_default: there's a {response.status_code} error with your request"
            )
        data = response.json()["MRData"]["RaceTable"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"result_default: there's a {response.status_code} error with your request"
        )
        return None


# the below has been updated
def previous_race():
    """API function for returning previous race before the most recent"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last", 
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")

        data = response.json()

        # if it's the first race of the season return the last race of last season
        previous_round = int((data)["round"])
        if previous_round <= 1:
            season = int((data)["season"])
            last_season = season - 1
            response2 = requests.get(
                f"https://f1connectapi.vercel.app/api/{last_season}/22", 
                timeout=120
            )
            if response2.status_code == 200:
                data1 = response2.json()
                return data1

        else:  # if after first race of season, return previous race of season
            if response.status_code == 200:
                return data
            else:
                return None

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            "previous_race: there's an error with your request"
        )
        return None

# the below has been updated
def next_race(number):
    """API function for returning nth next race from the last 
    (increments e.g 1 is next, 2 is the second race from now etc)"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last",
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"next_race: there's a {response.status_code} error with your request"
            )

        data = response.json()
        current_year = int(data["season"])
        current_round = int((data)["round"])

        if current_round >= 22:
            return False  # return false at end of season for app.py to use

        next_round = current_round + number  # takes the last race round and nth number argument
        response2 = requests.get(
            f"https://f1connectapi.vercel.app/api/{current_year}/{next_round}", timeout=120
        )
        if response2.status_code == 200:
            data1 = response2.json()
            return data1

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"next_race: there's a {response.status_code} error with your request")
        return None


# the below has been updated
def teams_lookup():
    """API function for returning all teams in current season"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/teams", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"teams_lookup: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return (data)["teams"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"teams_lookup: there's a {response.status_code} error with your request")
        return None


# the below has been updated
def drivers_lookup():
    """API function for returning all drivers in current season"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/drivers", timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"drivers_lookup: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return (data)["drivers"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"drivers_lookup: there's a {response.status_code} error with your request"
        )
        return None


# the below has been updated
def drivers_for_team(constructor):
    """API function for returning the drivers for a specific team"""
    try:
        response = requests.get(
            f"https://f1connectapi.vercel.app/api/current/teams/{constructor}/drivers", 
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"drivers_for_team: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return (data)["drivers"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"drivers_for_team: there's a {response.status_code} error with your request"
        )
        return None


# the below has been updated
def driver_standings():
    """API function for returning the drivers based on championship standing"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/drivers-championship", 
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"driver_standings: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data['drivers_championship']

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"driver_standings: there's a {response.status_code} error with your request"
        )
        return None


# the below has been updated
def team_standings():
    """API function for returning the teams based on championship standing"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/constructors-championship",
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(
                f"team_standings: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return (data)["constructors_championship"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"team_standings: there's a {response.status_code} error with your request"
        )
        return None


def lookup(driver, constructor):
    """API lookup for returning the different seasons a 
    certain driver has been with a certain team"""
    try:
        response = requests.get(
            f"http://ergast.com/api/f1/drivers/{driver}/constructors/{constructor}/seasons.json",
            timeout=120
        )
        if response.status_code == 200:
            print("successfully fetched the data")
        else:
            print(f"lookup: status code = {response.status_code}")
        return response.json()

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"lookup: there's a {response.status_code} error with your request")
        return None
