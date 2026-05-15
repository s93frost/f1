''' This file is storing all the function & API call functions for web app '''
import os
import re
import requests
import time
from threading import Thread
from functools import wraps
from datetime import datetime, timedelta

# Reuse a single User-Agent for both API and image downloads
HEADERS = {
    "User-Agent": "SffBot/0.0 (https://github.com/code50/47425976.git; sfproject@cs50.org)"
}

# Simple in-memory cache for API responses (TTL in seconds)
_cache = {}
CACHE_TTL = 86400  # 24 hours (API updates weekly)

def cache_api_response(ttl=CACHE_TTL):
    """Decorator to cache API function results with TTL"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if cache_key in _cache:
                result, timestamp = _cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl):
                    print(f"{func.__name__}: returning cached result (age: {(datetime.now() - timestamp).seconds}s)")
                    return result
                else:
                    del _cache[cache_key]
            
            result = func(*args, **kwargs)
            _cache[cache_key] = (result, datetime.now())
            return result
        return wrapper
    return decorator

def download_images_async(image_list, download_func):
    """Download multiple images in parallel using threads"""
    threads = []
    for image_data in image_list:
        thread = Thread(target=download_func, args=(image_data,), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Don't wait - let them run in background
    return threads

def clear_api_cache():
    """Manually clear the API response cache (useful for forcing a refresh)"""
    global _cache
    _cache.clear()
    print("API cache cleared")

def _download_driver_image(driver_data):
    """Background task for downloading a single driver image"""
    safe_name = _safe_filename(f'{driver_data["name"]}{driver_data["surname"]}')
    out_path = f'./static/driver_pics/{safe_name}.jpg'
    if os.path.isfile(out_path):
        return
    
    wiki_url = driver_data["url"]
    wiki_search_title = wiki_url.split("/")[-1]
    url = picture(wiki_search_title)
    if url:
        _download_image(url, out_path)

def _download_team_image(team_data):
    """Background task for downloading a single team image"""
    safe_team = _safe_filename(team_data["teamId"])
    out_path = f'./static/team_pics/{safe_team}.jpg'
    if os.path.isfile(out_path):
        return
    
    wiki_url = team_data["url"]
    wiki_search_title = wiki_url.split("/")[-1]
    url = picture(wiki_search_title)
    if url:
        _download_image(url, out_path)

def _download_track_image(race_data):
    """Background task for downloading a single track picture"""
    circuit = race_data.get('circuit', {})
    wiki_url = circuit.get('url') or race_data.get('url')
    if not wiki_url:
        return
    
    wiki_search_title = wiki_url.split("/")[-1]
    url = picture(wiki_search_title)
    if not url:
        return

    out_dir = os.path.join(".", "static", "track_pics")
    os.makedirs(out_dir, exist_ok=True)
    circuit_name = _safe_filename(circuit.get("circuitName", "track"))
    out_path = os.path.join(out_dir, f"{circuit_name}.jpg")

    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except requests.RequestException:
        pass
    except OSError:
        pass

def _download_race_image(race_data):
    """Background task for downloading a single race picture"""
    wiki_url = race_data.get('url')
    if not wiki_url:
        return
    
    wiki_search_title = wiki_url.split("/")[-1]
    url = picture(wiki_search_title)
    if not url:
        return

    out_dir = os.path.join(".", "static", "race_pics")
    os.makedirs(out_dir, exist_ok=True)
    race_name = _safe_filename(race_data.get('raceName', 'race'))
    out_path = os.path.join(out_dir, f"{race_name}.jpg")

    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except requests.RequestException:
        pass
    except OSError:
        pass

def picture(wiki_search_title):
    """MediaWiki API for returning main page image of an article - 
    used in conjuction with URL received from API"""
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&prop=pageimages|pageterms&piprop=thumbnail&pithumbsize=600&titles={wiki_search_title}&redirects=&pilicense=any"
        response = requests.get(url, headers=HEADERS, timeout=120)
        if response.status_code == 200:
            print("picture: successfully fetched the data")
        else:
            print(f"picture: there's a {response.status_code} error with your request")
        data = response.json()["query"]["pages"][0]["thumbnail"]["source"]
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"picture: there's a {response.status_code} error with your request")
        return None

def _safe_filename(name: str) -> str:
    '''Sanitize a string to be safe for use as a filename.'''
    # Replace anything unsafe for filenames
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('_') or "image"

def _download_image(url: str, out_path: str) -> bool:
    """Stream download an image with headers; returns True on success."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"[download] request failed: {e}")
    except OSError as e:
        print(f"[download] file write failed: {e}")
    return False

def track_pic(track):
    """function for getting track pictures using the circuit wiki page."""
    circuit = track['race'][0].get('circuit', {})
    wiki_url = circuit.get('url') or track['race'][0].get('url')
    wiki_search_title = wiki_url.split("/")[-1]
    url = picture(wiki_search_title)
    if not url:
        print("track_pic: no image url returned")
        return

    # Ensure output directory exists and filename is safe
    out_dir = os.path.join(".", "static", "track_pics")
    os.makedirs(out_dir, exist_ok=True)
    circuit_name = _safe_filename(circuit.get("circuitName", "track"))
    out_path = os.path.join(out_dir, f"{circuit_name}.jpg")

    try:
        # Download image with proper headers to avoid 403
        with requests.get(url, headers=HEADERS, stream=True, timeout=120) as resp:
            resp.raise_for_status()  # raises for 4xx/5xx
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"track_pic: saved {out_path}")
    except requests.HTTPError as e:
        print(f"track_pic: HTTP error downloading image ({e.response.status_code})")
    except requests.RequestException as e:
        print(f"track_pic: request failed ({e})")
    except OSError as e:
        print(f"track_pic: file write failed ({e})")


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def fastest(year, race):
    """API function for returning fastest driver in specified year and race"""
    try:
        response = requests.get(
            f"https://f1api.dev/api/{year}/{race}",
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def seasons_history():
    """API function for returning seasons available in API"""
    try:
        response = requests.get("https://f1api.dev/api/seasons?limit=100", timeout=120)
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
            f"https://f1api.dev/api/{year}?limit=100", timeout=120
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def result_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/last/race", 
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
            f"https://f1api.dev/api/{year}/{race}/race", 
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def qualifying_default():
    """API function for returning results of latest race"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/last/qualy", 
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
            f"https://f1api.dev/api/{year}/{race}/qualy", timeout=120
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def previous_race():
    """API function for returning previous race before the most recent"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/last", 
            timeout=120
        )
        if response.status_code == 200:
            print("previous_race: successfully fetched the data")

        data = response.json()

        # if it's the first race of the season return the last race of last season
        previous_round = int((data)["round"])
        if previous_round <= 0:
            season = int((data)["season"])
            last_season = season - 1
            response2 = requests.get(
                f"https://f1api.dev/api/{last_season}/24", 
                timeout=120
            )
            if response2.status_code == 200:
                data1 = response2.json()
                return data1

        else:  # if after first race of season, return previous race of this season
            if response.status_code == 200:
                return data
            else:
                return None

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            "previous_race: there's an error with your request"
        )
        return None


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def next_race(number):
    """API function for returning nth next race from the last 
    (increments e.g 1 is next, 2 is the second race from now etc)"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/last",
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
            f"https://f1api.dev/api/{current_year}/{next_round}", timeout=120
        )
        if response2.status_code == 200:
            data1 = response2.json()
            return data1

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(f"next_race: there's a {response.status_code} error with your request")
        return None


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def teams_lookup():
    """API function for returning all teams in current season"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/teams?limit=100", timeout=120
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def drivers_lookup():
    """API function for returning all drivers in current season"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/drivers?limit=100", timeout=120
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
    """Fetch all drivers by walking pages until the API clearly stops giving data."""
    all_drivers = []
    limit = 100
    offset = 0

    while True:
        try:
            response = requests.get(
                "https://f1connectapi.vercel.app/api/drivers",
                params={"limit": limit, "offset": offset},
                timeout=120,
            )

            # If we’ve gone past the end, API returns 404 → stop
            if response.status_code == 404:
                print(f"Reached end at offset {offset} (404)")
                break

            if response.status_code != 200:
                print(f"HTTP {response.status_code} at offset {offset}")
                break

            data = response.json()
            drivers = data.get("drivers", [])

            # No drivers at all → stop
            if not drivers:
                print(f"No drivers returned at offset {offset}, stopping.")
                break

            all_drivers.extend(drivers)

            # If we got fewer than limit, this is very likely the last page
            if len(drivers) < limit:
                print(f"Last page detected at offset {offset} (got {len(drivers)} < {limit})")
                break

            offset += limit

        except (requests.RequestException, ValueError) as e:
            print(f"Error at offset {offset}: {e}")
            break

    print(f"Total drivers fetched: {len(all_drivers)}")
    return all_drivers


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def drivers_for_team(constructor):
    """API function for returning the drivers for a specific team"""
    try:
        response = requests.get(
            f"https://f1api.dev/api/current/teams/{constructor}/drivers",
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


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def driver_standings():
    """API function for returning the drivers based on championship standing"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/drivers-championship", 
            timeout=120
        )
        if response.status_code == 200:
            print("driver_standings: successfully fetched the data")
        else:
            print(
                f"driver_standings: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"driver_standings: there's a {response.status_code} error with your request"
        )
        return None


def driver_standings_year(year):
    """API function for returning the drivers based on championship standing"""
    try:
        response = requests.get(
            f"https://f1api.dev/api/{year}/drivers-championship", 
            timeout=120
        )
        if response.status_code == 200:
            print("driver_standings_year: successfully fetched the data")
        else:
            print(
                f"driver_standings_year: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data['drivers_championship']

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"driver_standings_year: there's a {response.status_code} error with your request"
        )
        return None


@cache_api_response(ttl=86400)  # Cache for 24 hours (API updates weekly)
def team_standings():
    """API function for returning the teams based on championship standing"""
    try:
        response = requests.get(
            "https://f1api.dev/api/current/constructors-championship",
            timeout=120
        )
        if response.status_code == 200:
            print("team_standings: successfully fetched the data")
        else:
            print(
                f"team_standings: there's a {response.status_code} error with your request"
            )
        data = response.json()
        return data

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"team_standings: there's a {response.status_code} error with your request"
        )
        return None


def team_standings_year(year):
    """API function for returning the teams based on championship standing"""
    try:
        response = requests.get(
            f"https://f1api.dev/api/{year}/constructors-championship",
            timeout=120
        )
        if response.status_code == 200:
            print("team_standings_year: successfully fetched the data")

        data = response.json()
        return (data)["constructors_championship"]

    except (requests.RequestException, ValueError, KeyError, IndexError):
        print(
            f"team_standings_year: there's a {response.status_code} error with your request"
        )
        return None


def refresh_all_drivers(all_drivers_dict, drivers_all_years_func, previous_race_func, DRIVERS_SEASON=None, current_season=None):
    """Refresh all_drivers_dict and DRIVERS_SEASON, clearing dict first. Returns new DRIVERS_SEASON."""
    all_drivers_dict.clear()
    all_drivers = drivers_all_years_func()
    for driver in all_drivers:
        all_drivers_dict[driver["driverId"]] = driver
    if current_season:
        return current_season
    else:
        race = previous_race_func()
        if race and "season" in race:
            return race["season"]
    return DRIVERS_SEASON
