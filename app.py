''' This file is the application file serving the python logic for 
differnt routes and templates used by the web app'''

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
# dict storing seasons + race_name - not used anymore but kept to initiate line 234 - if not seasons_and_names:
seasons_and_names = {}
# dict for storing seasons, race_names + rounds for javascript options on results post - hard coded up to end of 2024 season and API used to pull and append data 2025 on
seasons_and_races = {2024: {'Gulf Air Bahrain Grand Prix 2024': 1, 'STC Saudi Arabian Grand Prix 2024': 2, 'Rolex Australian Grand Prix 2024': 3, 'MSC Cruises Japanese Grand Prix 2024': 4, 'Lenovo Chinese Grand Prix 2024': 5, 'Crypto.com Miami Grand Prix 2024': 6, 'Dell Emilia Romagna Grand Prix 2024': 7, 'Monaco 2024 Formula One Grand Prix': 8, 'AWS Grand Prix Du Canada 2024': 9, 'Aramco Gran Premio de España 2024': 10, 'Qatar Airways Austrian Grand Prix 2024': 11, 'Qatar Airways British Grand Prix 2024': 12, 'Hungarian Grand Prix 2024': 13, 'Rolex Belgian Grand Prix 2024': 14, 'Heineken Dutch Grand Prix 2024': 15, 'Pirelli Gran Premio D`Italia 2024': 16, 'Qatar Airways Azerbaijan Grand Prix 2024': 17, 'Singapore Airlines Singapore Grand Prix 2024': 18, 'Pirelli United States Grand Prix 2024': 19, 'Gran Premio de la Ciudad de Mexico 2024': 20, 'Lenovo Grande Premio de Sao Paulo 2024': 21, 'Heineken Silver Las Vegas Grand Prix 2024': 22, 'Qatar Airways Qatar Grand Prix 2024': 23, 'Etihad Airways Abu Dhabi Grand Prix 2024': 24}, 2023: {'Bahrain Grand Prix': 1, 'Saudi Arabian Grand Prix': 2, 'Australian Grand Prix': 3, 'Azerbaijan Grand Prix': 4, 'Miami Grand Prix': 5, 'Monaco Grand Prix': 6, 'Spanish Grand Prix': 7, 'Canadian Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Dutch Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Japanese Grand Prix': 16, 'Qatar Grand Prix': 17, 'United States Grand Prix': 18, 'Mexico City Grand Prix': 19, 'São Paulo Grand Prix': 20, 'Las Vegas Grand Prix': 21, 'Abu Dhabi Grand Prix': 22}, 2022: {'Bahrain Grand Prix': 1, 'Saudi Arabian Grand Prix': 2, 'Australian Grand Prix': 3, 'Emilia Romagna Grand Prix': 4, 'Miami Grand Prix': 5, 'Spanish Grand Prix': 6, 'Monaco Grand Prix': 7, 'Azerbaijan Grand Prix': 8, 'Canadian Grand Prix': 9, 'British Grand Prix': 10, 'Austrian Grand Prix': 11, 'French Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Belgian Grand Prix': 14, 'Dutch Grand Prix': 15, 'Italian Grand Prix': 16, 'Singapore Grand Prix': 17, 'Japanese Grand Prix': 18, 'United States Grand Prix': 19, 'Mexico City Grand Prix': 20, 'São Paulo Grand Prix': 21, 'Abu Dhabi Grand Prix': 22}, 2021: {'Bahrain Grand Prix': 1, 'Emilia Romagna Grand Prix': 2, 'Portuguese Grand Prix': 3, 'Spanish Grand Prix': 4, 'Monaco Grand Prix': 5, 'Azerbaijan Grand Prix': 6, 'French Grand Prix': 7, 'Styrian Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Dutch Grand Prix': 13, 'Italian Grand Prix': 14, 'Russian Grand Prix': 15, 'Turkish Grand Prix': 16, 'United States Grand Prix': 17, 'Mexico City Grand Prix': 18, 'São Paulo Grand Prix': 19, 'Qatar Grand Prix': 20, 'Saudi Arabian Grand Prix': 21, 'Abu Dhabi Grand Prix': 22}, 2020: {'Austrian Grand Prix': 1, 'Styrian Grand Prix': 2, 'Hungarian Grand Prix': 3, 'British Grand Prix': 4, '70th Anniversary Grand Prix': 5, 'Spanish Grand Prix': 6, 'Belgian Grand Prix': 7, 'Italian Grand Prix': 8, 'Tuscan Grand Prix': 9, 'Russian Grand Prix': 10, 'Eifel Grand Prix': 11, 'Portuguese Grand Prix': 12, 'Emilia Romagna Grand Prix': 13, 'Turkish Grand Prix': 14, 'Bahrain Grand Prix': 15, 'Sakhir Grand Prix': 16, 'Abu Dhabi Grand Prix': 17}, 2019: {'Australian Grand Prix': 1, 'Bahrain Grand Prix': 2, 'Chinese Grand Prix': 3, 'Azerbaijan Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Russian Grand Prix': 16, 'Japanese Grand Prix': 17, 'Mexican Grand Prix': 18, 'United States Grand Prix': 19, 'Brazilian Grand Prix': 20, 'Abu Dhabi Grand Prix': 21}, 2018: {'Australian Grand Prix': 1, 'Bahrain Grand Prix': 2, 'Chinese Grand Prix': 3, 'Azerbaijan Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Russian Grand Prix': 16, 'Japanese Grand Prix': 17, 'United States Grand Prix': 18, 'Mexican Grand Prix': 19, 'Brazilian Grand Prix': 20, 'Abu Dhabi Grand Prix': 21}, 2017: {'Australian Grand Prix': 1, 'Chinese Grand Prix': 2, 'Bahrain Grand Prix': 3, 'Russian Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'Azerbaijan Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Singapore Grand Prix': 14, 'Malaysian Grand Prix': 15, 'Japanese Grand Prix': 16, 'United States Grand Prix': 17, 'Mexican Grand Prix': 18, 'Brazilian Grand Prix': 19, 'Abu Dhabi Grand Prix': 20}, 2016: {'Australian Grand Prix': 1, 'Bahrain Grand Prix': 2, 'Chinese Grand Prix': 3, 'Russian Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'European Grand Prix': 8, 'Austrian Grand Prix': 9, 'British Grand Prix': 10, 'Hungarian Grand Prix': 11, 'German Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Malaysian Grand Prix': 16, 'Japanese Grand Prix': 17, 'United States Grand Prix': 18, 'Mexican Grand Prix': 19, 'Brazilian Grand Prix': 20, 'Abu Dhabi Grand Prix': 21}, 2015: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Chinese Grand Prix': 3, 'Bahrain Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'Austrian Grand Prix': 8, 'British Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Singapore Grand Prix': 13, 'Japanese Grand Prix': 14, 'Russian Grand Prix': 15, 'United States Grand Prix': 16, 'Mexican Grand Prix': 17, 'Brazilian Grand Prix': 18, 'Abu Dhabi Grand Prix': 19}, 2014: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Bahrain Grand Prix': 3, 'Chinese Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'Austrian Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Singapore Grand Prix': 14, 'Japanese Grand Prix': 15, 'Russian Grand Prix': 16, 'United States Grand Prix': 17, 'Brazilian Grand Prix': 18, 'Abu Dhabi Grand Prix': 19}, 2013: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Chinese Grand Prix': 3, 'Bahrain Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Singapore Grand Prix': 13, 'Korean Grand Prix': 14, 'Japanese Grand Prix': 15, 'Indian Grand Prix': 16, 'Abu Dhabi Grand Prix': 17, 'United States Grand Prix': 18, 'Brazilian Grand Prix': 19}, 2012: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Chinese Grand Prix': 3, 'Bahrain Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'European Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Singapore Grand Prix': 14, 'Japanese Grand Prix': 15, 'Korean Grand Prix': 16, 'Indian Grand Prix': 17, 'Abu Dhabi Grand Prix': 18, 'United States Grand Prix': 19, 'Brazilian Grand Prix': 20}, 2011: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Chinese Grand Prix': 3, 'Turkish Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'European Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Singapore Grand Prix': 14, 'Japanese Grand Prix': 15, 'Korean Grand Prix': 16, 'Indian Grand Prix': 17, 'Abu Dhabi Grand Prix': 18, 'Brazilian Grand Prix': 19}, 2010: {'Bahrain Grand Prix': 1, 'Australian Grand Prix': 2, 'Malaysian Grand Prix': 3, 'Chinese Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Turkish Grand Prix': 7, 'Canadian Grand Prix': 8, 'European Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Japanese Grand Prix': 16, 'Korean Grand Prix': 17, 'Brazilian Grand Prix': 18, 'Abu Dhabi Grand Prix': 19}, 2009: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Chinese Grand Prix': 3, 'Bahrain Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Turkish Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'European Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Singapore Grand Prix': 14, 'Japanese Grand Prix': 15, 'Brazilian Grand Prix': 16, 'Abu Dhabi Grand Prix': 17}, 2008: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Bahrain Grand Prix': 3, 'Spanish Grand Prix': 4, 'Turkish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'European Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Singapore Grand Prix': 15, 'Japanese Grand Prix': 16, 'Chinese Grand Prix': 17, 'Brazilian Grand Prix': 18}, 2007: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Bahrain Grand Prix': 3, 'Spanish Grand Prix': 4, 'Monaco Grand Prix': 5, 'Canadian Grand Prix': 6, 'United States Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'European Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Turkish Grand Prix': 12, 'Italian Grand Prix': 13, 'Belgian Grand Prix': 14, 'Japanese Grand Prix': 15, 'Chinese Grand Prix': 16, 'Brazilian Grand Prix': 17}, 2006: {'Bahrain Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Australian Grand Prix': 3, 'San Marino Grand Prix': 4, 'European Grand Prix': 5, 'Spanish Grand Prix': 6, 'Monaco Grand Prix': 7, 'British Grand Prix': 8, 'Canadian Grand Prix': 9, 'United States Grand Prix': 10, 'French Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Turkish Grand Prix': 14, 'Italian Grand Prix': 15, 'Chinese Grand Prix': 16, 'Japanese Grand Prix': 17, 'Brazilian Grand Prix': 18}, 2005: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Bahrain Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'European Grand Prix': 7, 'Canadian Grand Prix': 8, 'United States Grand Prix': 9, 'French Grand Prix': 10, 'British Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Turkish Grand Prix': 14, 'Italian Grand Prix': 15, 'Belgian Grand Prix': 16, 'Brazilian Grand Prix': 17, 'Japanese Grand Prix': 18, 'Chinese Grand Prix': 19}, 2004: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Bahrain Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'European Grand Prix': 7, 'Canadian Grand Prix': 8, 'United States Grand Prix': 9, 'French Grand Prix': 10, 'British Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Belgian Grand Prix': 14, 'Italian Grand Prix': 15, 'Chinese Grand Prix': 16, 'Japanese Grand Prix': 17, 'Brazilian Grand Prix': 18}, 2003: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Brazilian Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Austrian Grand Prix': 6, 'Monaco Grand Prix': 7, 'Canadian Grand Prix': 8, 'European Grand Prix': 9, 'French Grand Prix': 10, 'British Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Italian Grand Prix': 14, 'United States Grand Prix': 15, 'Japanese Grand Prix': 16}, 2002: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Brazilian Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Austrian Grand Prix': 6, 'Monaco Grand Prix': 7, 'Canadian Grand Prix': 8, 'European Grand Prix': 9, 'British Grand Prix': 10, 'French Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Belgian Grand Prix': 14, 'Italian Grand Prix': 15, 'United States Grand Prix': 16, 'Japanese Grand Prix': 17}, 2001: {'Australian Grand Prix': 1, 'Malaysian Grand Prix': 2, 'Brazilian Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Austrian Grand Prix': 6, 'Monaco Grand Prix': 7, 'Canadian Grand Prix': 8, 'European Grand Prix': 9, 'French Grand Prix': 10, 'British Grand Prix': 11, 'German Grand Prix': 12, 'Hungarian Grand Prix': 13, 'Belgian Grand Prix': 14, 'Italian Grand Prix': 15, 'United States Grand Prix': 16, 'Japanese Grand Prix': 17}, 2000: {'Australian Grand Prix': 1, 'Brazilian Grand Prix': 2, 'San Marino Grand Prix': 3, 'British Grand Prix': 4, 'Spanish Grand Prix': 5, 'European Grand Prix': 6, 'Monaco Grand Prix': 7, 'Canadian Grand Prix': 8, 'French Grand Prix': 9, 'Austrian Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'United States Grand Prix': 15, 'Japanese Grand Prix': 16, 'Malaysian Grand Prix': 17}, 1999: {'Australian Grand Prix': 1, 'Brazilian Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Spanish Grand Prix': 5, 'Canadian Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'Austrian Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'European Grand Prix': 14, 'Malaysian Grand Prix': 15, 'Japanese Grand Prix': 16}, 1998: {'Australian Grand Prix': 1, 'Brazilian Grand Prix': 2, 'Argentine Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'Austrian Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Luxembourg Grand Prix': 15, 'Japanese Grand Prix': 16}, 1997: {'Australian Grand Prix': 1, 'Brazilian Grand Prix': 2, 'Argentine Grand Prix': 3, 'San Marino Grand Prix': 4, 'Monaco Grand Prix': 5, 'Spanish Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Austrian Grand Prix': 14, 'Luxembourg Grand Prix': 15, 'Japanese Grand Prix': 16, 'European Grand Prix': 17}, 1996: {'Australian Grand Prix': 1, 'Brazilian Grand Prix': 2, 'Argentine Grand Prix': 3, 'European Grand Prix': 4, 'San Marino Grand Prix': 5, 'Monaco Grand Prix': 6, 'Spanish Grand Prix': 7, 'Canadian Grand Prix': 8, 'French Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Hungarian Grand Prix': 12, 'Belgian Grand Prix': 13, 'Italian Grand Prix': 14, 'Portuguese Grand Prix': 15, 'Japanese Grand Prix': 16}, 1995: {'Brazilian Grand Prix': 1, 'Argentine Grand Prix': 2, 'San Marino Grand Prix': 3, 'Spanish Grand Prix': 4, 'Monaco Grand Prix': 5, 'Canadian Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'European Grand Prix': 14, 'Pacific Grand Prix': 15, 'Japanese Grand Prix': 16, 'Australian Grand Prix': 17}, 1994: {'Brazilian Grand Prix': 1, 'Pacific Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Spanish Grand Prix': 5, 'Canadian Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'European Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1993: {'South African Grand Prix': 1, 'Brazilian Grand Prix': 2, 'European Grand Prix': 3, 'San Marino Grand Prix': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Portuguese Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1992: {'South African Grand Prix': 1, 'Mexican Grand Prix': 2, 'Brazilian Grand Prix': 3, 'Spanish Grand Prix': 4, 'San Marino Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Belgian Grand Prix': 12, 'Italian Grand Prix': 13, 'Portuguese Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1991: {'United States Grand Prix': 1, 'Brazilian Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Canadian Grand Prix': 5, 'Mexican Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'Spanish Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1990: {'United States Grand Prix': 1, 'Brazilian Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Canadian Grand Prix': 5, 'Mexican Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'Spanish Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1989: {'Brazilian Grand Prix': 1, 'San Marino Grand Prix': 2, 'Monaco Grand Prix': 3, 'Mexican Grand Prix': 4, 'United States Grand Prix': 5, 'Canadian Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'Spanish Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1988: {'Brazilian Grand Prix': 1, 'San Marino Grand Prix': 2, 'Monaco Grand Prix': 3, 'Mexican Grand Prix': 4, 'Canadian Grand Prix': 5, 'Detroit Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Hungarian Grand Prix': 10, 'Belgian Grand Prix': 11, 'Italian Grand Prix': 12, 'Portuguese Grand Prix': 13, 'Spanish Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1987: {'Brazilian Grand Prix': 1, 'San Marino Grand Prix': 2, 'Belgian Grand Prix': 3, 'Monaco Grand Prix': 4, 'Detroit Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'German Grand Prix': 8, 'Hungarian Grand Prix': 9, 'Austrian Grand Prix': 10, 'Italian Grand Prix': 11, 'Portuguese Grand Prix': 12, 'Spanish Grand Prix': 13, 'Mexican Grand Prix': 14, 'Japanese Grand Prix': 15, 'Australian Grand Prix': 16}, 1986: {'Brazilian Grand Prix': 1, 'Spanish Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Belgian Grand Prix': 5, 'Canadian Grand Prix': 6, 'Detroit Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Hungarian Grand Prix': 11, 'Austrian Grand Prix': 12, 'Italian Grand Prix': 13, 'Portuguese Grand Prix': 14, 'Mexican Grand Prix': 15, 'Australian Grand Prix': 16}, 1985: {'Brazilian Grand Prix': 1, 'Portuguese Grand Prix': 2, 'San Marino Grand Prix': 3, 'Monaco Grand Prix': 4, 'Canadian Grand Prix': 5, 'Detroit Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Austrian Grand Prix': 10, 'Dutch Grand Prix': 11, 'Italian Grand Prix': 12, 'Belgian Grand Prix': 13, 'European Grand Prix': 14, 'South African Grand Prix': 15, 'Australian Grand Prix': 16}, 1984: {'Brazilian Grand Prix': 1, 'South African Grand Prix': 2, 'Belgian Grand Prix': 3, 'San Marino Grand Prix': 4, 'French Grand Prix': 5, 'Monaco Grand Prix': 6, 'Canadian Grand Prix': 7, 'Detroit Grand Prix': 8, 'Dallas Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Dutch Grand Prix': 13, 'Italian Grand Prix': 14, 'European Grand Prix': 15, 'Portuguese Grand Prix': 16}, 1983: {'Brazilian Grand Prix': 1, 'United States Grand Prix West': 2, 'French Grand Prix': 3, 'San Marino Grand Prix': 4, 'Monaco Grand Prix': 5, 'Belgian Grand Prix': 6, 'Detroit Grand Prix': 7, 'Canadian Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Austrian Grand Prix': 11, 'Dutch Grand Prix': 12, 'Italian Grand Prix': 13, 'European Grand Prix': 14, 'South African Grand Prix': 15}, 1982: {'South African Grand Prix': 1, 'Brazilian Grand Prix': 2, 'United States Grand Prix West': 3, 'San Marino Grand Prix': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'Detroit Grand Prix': 7, 'Canadian Grand Prix': 8, 'Dutch Grand Prix': 9, 'British Grand Prix': 10, 'French Grand Prix': 11, 'German Grand Prix': 12, 'Austrian Grand Prix': 13, 'Swiss Grand Prix': 14, 'Italian Grand Prix': 15, 'Caesars Palace Grand Prix': 16}, 1981: {'United States Grand Prix West': 1, 'Brazilian Grand Prix': 2, 'Argentine Grand Prix': 3, 'San Marino Grand Prix': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'Spanish Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Austrian Grand Prix': 11, 'Dutch Grand Prix': 12, 'Italian Grand Prix': 13, 'Canadian Grand Prix': 14, 'Caesars Palace Grand Prix': 15}, 1980: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'United States Grand Prix West': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'French Grand Prix': 7, 'British Grand Prix': 8, 'German Grand Prix': 9, 'Austrian Grand Prix': 10, 'Dutch Grand Prix': 11, 'Italian Grand Prix': 12, 'Canadian Grand Prix': 13, 'United States Grand Prix': 14}, 1979: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'United States Grand Prix West': 4, 'Spanish Grand Prix': 5, 'Belgian Grand Prix': 6, 'Monaco Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Austrian Grand Prix': 11, 'Dutch Grand Prix': 12, 'Italian Grand Prix': 13, 'Canadian Grand Prix': 14, 'United States Grand Prix': 15}, 1978: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'United States Grand Prix West': 4, 'Monaco Grand Prix': 5, 'Belgian Grand Prix': 6, 'Spanish Grand Prix': 7, 'Swedish Grand Prix': 8, 'French Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Dutch Grand Prix': 13, 'Italian Grand Prix': 14, 'United States Grand Prix': 15, 'Canadian Grand Prix': 16}, 1977: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'United States Grand Prix West': 4, 'Spanish Grand Prix': 5, 'Monaco Grand Prix': 6, 'Belgian Grand Prix': 7, 'Swedish Grand Prix': 8, 'French Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Dutch Grand Prix': 13, 'Italian Grand Prix': 14, 'United States Grand Prix': 15, 'Canadian Grand Prix': 16, 'Japanese Grand Prix': 17}, 1976: {'Brazilian Grand Prix': 1, 'South African Grand Prix': 2, 'United States Grand Prix West': 3, 'Spanish Grand Prix': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'Swedish Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'German Grand Prix': 10, 'Austrian Grand Prix': 11, 'Dutch Grand Prix': 12, 'Italian Grand Prix': 13, 'Canadian Grand Prix': 14, 'United States Grand Prix': 15, 'Japanese Grand Prix': 16}, 1975: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'Spanish Grand Prix': 4, 'Monaco Grand Prix': 5, 'Belgian Grand Prix': 6, 'Swedish Grand Prix': 7, 'Dutch Grand Prix': 8, 'French Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Italian Grand Prix': 13, 'United States Grand Prix': 14}, 1974: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'Spanish Grand Prix': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'Swedish Grand Prix': 7, 'Dutch Grand Prix': 8, 'French Grand Prix': 9, 'British Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Italian Grand Prix': 13, 'Canadian Grand Prix': 14, 'United States Grand Prix': 15}, 1973: {'Argentine Grand Prix': 1, 'Brazilian Grand Prix': 2, 'South African Grand Prix': 3, 'Spanish Grand Prix': 4, 'Belgian Grand Prix': 5, 'Monaco Grand Prix': 6, 'Swedish Grand Prix': 7, 'French Grand Prix': 8, 'British Grand Prix': 9, 'Dutch Grand Prix': 10, 'German Grand Prix': 11, 'Austrian Grand Prix': 12, 'Italian Grand Prix': 13, 'Canadian Grand Prix': 14, 'United States Grand Prix': 15}, 1972: {'Argentine Grand Prix': 1, 'South African Grand Prix': 2, 'Spanish Grand Prix': 3, 'Monaco Grand Prix': 4, 'Belgian Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'German Grand Prix': 8, 'Austrian Grand Prix': 9, 'Italian Grand Prix': 10, 'Canadian Grand Prix': 11, 'United States Grand Prix': 12}, 1971: {'South African Grand Prix': 1, 'Spanish Grand Prix': 2, 'Monaco Grand Prix': 3, 'Dutch Grand Prix': 4, 'French Grand Prix': 5, 'British Grand Prix': 6, 'German Grand Prix': 7, 'Austrian Grand Prix': 8, 'Italian Grand Prix': 9, 'Canadian Grand Prix': 10, 'United States Grand Prix': 11}, 1970: {'South African Grand Prix': 1, 'Spanish Grand Prix': 2, 'Monaco Grand Prix': 3, 'Belgian Grand Prix': 4, 'Dutch Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'German Grand Prix': 8, 'Austrian Grand Prix': 9, 'Italian Grand Prix': 10, 'Canadian Grand Prix': 11, 'United States Grand Prix': 12, 'Mexican Grand Prix': 13}, 1969: {'South African Grand Prix': 1, 'Spanish Grand Prix': 2, 'Monaco Grand Prix': 3, 'Dutch Grand Prix': 4, 'French Grand Prix': 5, 'British Grand Prix': 6, 'German Grand Prix': 7, 'Italian Grand Prix': 8, 'Canadian Grand Prix': 9, 'United States Grand Prix': 10, 'Mexican Grand Prix': 11}, 1968: {'South African Grand Prix': 1, 'Spanish Grand Prix': 2, 'Monaco Grand Prix': 3, 'Belgian Grand Prix': 4, 'Dutch Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'German Grand Prix': 8, 'Italian Grand Prix': 9, 'Canadian Grand Prix': 10, 'United States Grand Prix': 11, 'Mexican Grand Prix': 12}, 1967: {'South African Grand Prix': 1, 'Monaco Grand Prix': 2, 'Dutch Grand Prix': 3, 'Belgian Grand Prix': 4, 'French Grand Prix': 5, 'British Grand Prix': 6, 'German Grand Prix': 7, 'Canadian Grand Prix': 8, 'Italian Grand Prix': 9, 'United States Grand Prix': 10, 'Mexican Grand Prix': 11}, 1966: {'Monaco Grand Prix': 1, 'Belgian Grand Prix': 2, 'French Grand Prix': 3, 'British Grand Prix': 4, 'Dutch Grand Prix': 5, 'German Grand Prix': 6, 'Italian Grand Prix': 7, 'United States Grand Prix': 8, 'Mexican Grand Prix': 9}, 1965: {'South African Grand Prix': 1, 'Monaco Grand Prix': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'Dutch Grand Prix': 6, 'German Grand Prix': 7, 'Italian Grand Prix': 8, 'United States Grand Prix': 9, 'Mexican Grand Prix': 10}, 1964: {'Monaco Grand Prix': 1, 'Dutch Grand Prix': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Austrian Grand Prix': 7, 'Italian Grand Prix': 8, 'United States Grand Prix': 9, 'Mexican Grand Prix': 10}, 1963: {'Monaco Grand Prix': 1, 'Belgian Grand Prix': 2, 'Dutch Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Italian Grand Prix': 7, 'United States Grand Prix': 8, 'Mexican Grand Prix': 9, 'South African Grand Prix': 10}, 1962: {'Dutch Grand Prix': 1, 'Monaco Grand Prix': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Italian Grand Prix': 7, 'United States Grand Prix': 8, 'South African Grand Prix': 9}, 1961: {'Monaco Grand Prix': 1, 'Dutch Grand Prix': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Italian Grand Prix': 7, 'United States Grand Prix': 8}, 1960: {'Argentine Grand Prix': 1, 'Monaco Grand Prix': 2, 'Indianapolis 500': 3, 'Dutch Grand Prix': 4, 'Belgian Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'Portuguese Grand Prix': 8, 'Italian Grand Prix': 9, 'United States Grand Prix': 10}, 1959: {'Monaco Grand Prix': 1, 'Indianapolis 500': 2, 'Dutch Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Portuguese Grand Prix': 7, 'Italian Grand Prix': 8, 'United States Grand Prix': 9}, 1958: {'Argentine Grand Prix': 1, 'Monaco Grand Prix': 2, 'Dutch Grand Prix': 3, 'Indianapolis 500': 4, 'Belgian Grand Prix': 5, 'French Grand Prix': 6, 'British Grand Prix': 7, 'German Grand Prix': 8, 'Portuguese Grand Prix': 9, 'Italian Grand Prix': 10, 'Moroccan Grand Prix': 11}, 1957: {'Argentine Grand Prix': 1, 'Monaco Grand Prix': 2, 'Indianapolis 500': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Pescara Grand Prix': 7, 'Italian Grand Prix': 8}, 1956: {'Argentine Grand Prix': 1, 'Monaco Grand Prix': 2, 'Indianapolis 500': 3, 'Belgian Grand Prix': 4, 'French Grand Prix': 5, 'British Grand Prix': 6, 'German Grand Prix': 7, 'Italian Grand Prix': 8}, 1955: {'Argentine Grand Prix': 1, 'Monaco Grand Prix': 2, 'Indianapolis 500': 3, 'Belgian Grand Prix': 4, 'Dutch Grand Prix': 5, 'British Grand Prix': 6, 'Italian Grand Prix': 7}, 1954: {'Argentine Grand Prix': 1, 'Indianapolis 500': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Swiss Grand Prix': 7, 'Italian Grand Prix': 8, 'Spanish Grand Prix': 9}, 1953: {'Argentine Grand Prix': 1, 'Indianapolis 500': 2, 'Dutch Grand Prix': 3, 'Belgian Grand Prix': 4, 'French Grand Prix': 5, 'British Grand Prix': 6, 'German Grand Prix': 7, 'Swiss Grand Prix': 8, 'Italian Grand Prix': 9}, 1952: {'Swiss Grand Prix': 1, 'Indianapolis 500': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Dutch Grand Prix': 7, 'Italian Grand Prix': 8}, 1951: {'Swiss Grand Prix': 1, 'Indianapolis 500': 2, 'Belgian Grand Prix': 3, 'French Grand Prix': 4, 'British Grand Prix': 5, 'German Grand Prix': 6, 'Italian Grand Prix': 7, 'Spanish Grand Prix': 8}, 1950: {'British Grand Prix': 1, 'Monaco Grand Prix': 2, 'Indianapolis 500': 3, 'Swiss Grand Prix': 4, 'Belgian Grand Prix': 5, 'French Grand Prix': 6, 'Italian Grand Prix': 7}}


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
            drivers_and_teams[team] = []
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

        fastest_lap = fastest(year, race_round)  # for getting fastest lap of selected race
        selected_data = result(year, race_round)  # for getting result data for selected race
        qualify = qualifying(year, race_round)  # for getting qualy data for selected race

        try:
            qualify_data = qualify["races"]

        except (ValueError, KeyError, IndexError):
            qualify = None
            qualify_data = None

        try:
            result_data = selected_data["races"]
            wiki_url = selected_data["races"]["url"] # to pull picture for race
            wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
            url = picture(wiki_search_title) # uses title for API function search to pull picture
            if url:
                urllib.request.urlretrieve(
                    url,
                    f'./static/race_pics/{selected_data["races"]["raceName"]}.jpg',
                )

        except (ValueError, KeyError, IndexError):
            result_data = None

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
        )

    # if not post but get method
    else:
        current = result_default()
        qualify = qualifying_default()

        # below checks to see if season hasnt been built yet and adds a hardcoded default to show
        try:
            data = result(current["season"], current["round"])
            fastest_lap = fastest(current["season"], current["round"]) # get fastest lap of race
            qualify = qualifying_default()
            qualify_data = qualify["races"]
        except (ValueError, KeyError, IndexError):
            data = result(2024, 24)
            fastest_lap = fastest(2024, 24) # get fastest lap of race
            qualify = qualifying(2024, 24)

        wiki_url = data["races"]["url"] # to pull picture for specific race loaded on page
        wiki_search_title = wiki_url.split("/")[-1] # splits out page title for API search
        url = picture(wiki_search_title) # uses title for API function search tp pull picture
        if url:
            urllib.request.urlretrieve(
                url,
                f'./static/race_pics/{data["races"]["raceName"]}.jpg',
            )

        result_data = data["races"]
        qualify_data = qualify["races"]

        return render_template(
            "results.html",
            seasons_and_races=seasons_and_races,
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
                d = driver["driver"]["name"] + " " + driver["driver"]["surname"]
                names_dict[team_name].append(d)

    # dict to store values of driver ids and names
    driver_names = {}
    for driver in drivers_dict.values():
        drivername = driver["name"] + " " + driver["surname"]
        driver_names[drivername] = driver["driverId"]

    # dict to store vaues of driver ids and names
    team_names = {}
    for team in teams_dict.values():
        tname = team["teamName"]
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


        return render_template(
            "driver_history.html",
            names_dict=names_dict,
            drivers_name=drivers_name,
            constructor_name=constructor_name,
            CURRENT_SEASON=CURRENT_SEASON,
        )

    # if method = GET
    else:
        constructor_name = ""
        drivers_name = ""

        return render_template(
            "driver_history.html",
            names_dict=names_dict,
            drivers_name=drivers_name,
            constructor_name=constructor_name,
            CURRENT_SEASON=CURRENT_SEASON,
        )
