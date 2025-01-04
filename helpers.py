''' This file is storing all the function & API call functions for web app '''
import urllib
import requests


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
            print("picture: successfully fetched the data")
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
            f"https://f1connectapi.vercel.app/api/{year}/{race}",
            timeout=120
        )
        if response.status_code == 200:
            print("fastest: successfully fetched the data")
        else:
            print(f"fastest: there's a {response.status_code} error with your request")
        data = response.json()["race"][0]["fast_lap"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"fastest: there's a {response.status_code} error with your request")
        return None


def seasons_history():
    """API function for returning seasons available in API"""
    try:
        response = requests.get("https://f1connectapi.vercel.app/api/seasons?limit=99", timeout=120)
        if response.status_code == 200:
            print("seasons_history: successfully fetched the data")
        else:
            print(
                f"seasons_history: there's a {response.status_code} error with your request"
            )
        data = response.json()["championships"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"seasons_history: there's a {response.status_code} error with your request"
        )
        return None


def races(year):
    """API function for returning races of a specific season available in API"""
    try:
        response = requests.get(
            f"https://f1connectapi.vercel.app/api/{year}?limit=100", timeout=120
        )
        if response.status_code == 200:
            print("races: successfully fetched the data")
        else:
            print(
                f"races: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"races: there's a {response.status_code} error with your request"
        )
        return None


def result_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last", 
            timeout=120
        )
        if response.status_code == 200:
            print("result_default: successfully fetched the data")
        else:
            print(
                f"result_default: there's a {response.status_code} error with your request"
            )
        data = response.json()
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
            f"https://f1connectapi.vercel.app/api/{year}/{race}/race", 
            timeout=120
        )
        if response.status_code == 200:
            print("result: successfully fetched the data")
        else:
            print(f"result: there's a {response.status_code} error with your request")
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"result: there's a {response.status_code} error with your request")
        return None


def qualifying_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last/qualy", 
            timeout=120
        )
        if response.status_code == 200:
            print("qualifying_default: successfully fetched the data")
        else:
            print(
                f"qualifying_default: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"qualifying_default: there's a {response.status_code} error with your request"
        )
        return None


def qualifying(year, race):
    """API function for returning results from a specific race by season and race"""
    try:
        response = requests.get(
            f"https://f1connectapi.vercel.app/api/{year}/{race}/qualy", timeout=120
        )
        if response.status_code == 200:
            print("qualifying: successfully fetched the data")
        else:
            print(f"qualifying: there's a {response.status_code} error with your request")
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"qualifying: there's a {response.status_code} error with your request")
        return None


def previous_race():
    """API function for returning previous race before the most recent"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last", 
            timeout=120
        )
        if response.status_code == 200:
            print("previous_race: successfully fetched the data")

        data = response.json()

        # if it's the first race of the season return the last race of last season
        previous_round = int((data)["round"])
        if previous_round <= 1:
            season = int((data)["season"])
            last_season = season - 1
            response2 = requests.get(
                f"https://f1connectapi.vercel.app/api/{last_season}/24", 
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


def next_race(number):
    """API function for returning nth next race from the last 
    (increments e.g 1 is next, 2 is the second race from now etc)"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/last",
            timeout=120
        )
        if response.status_code == 200:
            print(f"next_race + {number}: successfully fetched the data")
        else:
            print(
                f"next_race: there's a {response.status_code} error with your request"
            )

        data = response.json()
        current_year = int(data["season"])
        current_round = int((data)["round"])

        if current_round >= 24:
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


def teams_lookup():
    """API function for returning all teams in current season"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/teams?limit=100", timeout=120
        )
        if response.status_code == 200:
            print("teams_lookup: successfully fetched the data")
        else:
            print(
                f"teams_lookup: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return (data)["teams"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"teams_lookup: there's a {response.status_code} error with your request")
        return None


def drivers_lookup():
    """API function for returning all drivers in current season"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/drivers?limit=100", timeout=120
        )
        if response.status_code == 200:
            print("drivers_lookup: successfully fetched the data")
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

def drivers_all_years():
    """API function for returning all drivers in all seasons"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/drivers?limit=1000", timeout=120
        )
        if response.status_code == 200:
            print("drivers_lookup: successfully fetched the data")
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


def drivers_for_team(constructor):
    """API function for returning the drivers for a specific team"""
    try:
        response = requests.get(
            f"https://f1connectapi.vercel.app/api/current/teams/{constructor}/drivers", 
            timeout=120
        )
        if response.status_code == 200:
            print("drivers_for_team: successfully fetched the data")
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


def driver_standings():
    """API function for returning the drivers based on championship standing"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/drivers-championship", 
            timeout=120
        )
        if response.status_code == 200:
            print("driver_standings: successfully fetched the data")
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


def team_standings():
    """API function for returning the teams based on championship standing"""
    try:
        response = requests.get(
            "https://f1connectapi.vercel.app/api/current/constructors-championship",
            timeout=120
        )
        if response.status_code == 200:
            print("team_standings: successfully fetched the data")
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
            print("lookup: successfully fetched the data")
        else:
            print(f"lookup: status code = {response.status_code}")
        return response.json()

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"lookup: there's a {response.status_code} error with your request")
        return None
