"""
This script pulls a data dump from the Fantasy.PremierLeague.com site,
extracts the goal scorer data for each football player, and updates the
database tables that record number of goals scored by player and
timestamps by goal.
"""

from datetime import datetime
import numpy as np
import pandas as pd
import psycopg2
import requests
import sys

sys.path.insert(1, 'E:/Code/f2t/app')

import secrets as sec


# Section 1 - Pull player data from app database
# Update tables in database
conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
  sec.db, sec.user, sec.pw, sec.host))

cur = conn.cursor()

# Get current player data
cur.execute("SELECT * FROM app.player;")
players = cur.fetchall()
players = pd.DataFrame(players)

# Set column names
col_names = ('player_id', 'first_name', 'second_name', 'goals_scored',
             'created_on')
players.columns = col_names

cur.close()
conn.close()


# Section 2 - Pull updated goal scorers from Fantasy.PremierLeague.com
# Pull data from Fantasy.PremierLeague.com
URL = 'https://fantasy.premierleague.com/api/bootstrap-static/'
RESPONSE = requests.get(URL)
ELEMENTS = RESPONSE.json()['elements']

# Extract player id and first and last name to a DataFrame
new_players = pd.DataFrame(np.empty((len(ELEMENTS), 4)))
new_players[:] = np.nan
new_players.columns = ['player_id', 'first_name', 'second_name',
                       'goals_scored']

for i, item in enumerate(ELEMENTS):
    new_players.iloc[i, 0] = int(item['id'])
    new_players.iloc[i, 1] = str(item['first_name'])
    new_players.iloc[i, 2] = str(item['second_name'])
    new_players.iloc[i, 3] = int(item['goals_scored'])

# Sort data by ID to make it comparable
new_players.astype({'player_id': 'int64', 'goals_scored': 'int64'})
new_players.sort_values(by=['player_id'])
new_players.sort_index(inplace=True)

# Write data to file as record
NOW = datetime.now().strftime("%Y-%m-%S_%H-%M-%S")
FILE = 'data/update_goals/goals_{}.csv'.format(NOW)
new_players.to_csv(FILE, encoding='utf-8', index=False)


# Section 3 - Compare existing goal scoreres data to updated data and store
# new goal scorer timestamps in app database
joint_scorers = pd.merge(players, new_players, on='player_id')
goal_diff = joint_scorers['goals_scored_x'] != joint_scorers['goals_scored_y']
new_scorers = joint_scorers[goal_diff]

# Only need id, first name, and last name of goal scorers
gs_col_names = ['player_id', 'first_name_x', 'second_name_x']
gs_table_cols = ('player_id', 'first_name', 'second_name')
new_scorers = new_scorers[gs_col_names]

# Write goal scored to file as record
gs_NOW = datetime.now().strftime("%Y-%m-%S_%H-%M-%S")
gs_FILE = 'data/update_goal_scored/goal_scored_{}.csv'.format(gs_NOW)
new_scorers.to_csv(gs_FILE, encoding='utf-8', index=False)

conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
  sec.db, sec.user, sec.pw, sec.host))

cur = conn.cursor()

with open(gs_FILE, 'r', encoding='utf-8') as row:
    next(row)  # Skip header row
    cur.copy_from(row, 'app.goal_scored', sep=',', columns=gs_table_cols)

conn.commit()

cur.close()
conn.close()
