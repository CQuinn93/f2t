"""
This script pulls a data dump from the Fantasy.PremierLeague.com site,
extracts the goal scorer data for each football player, and updates the
database tables that record number of goals scored by player and
timestamps by goal.
"""

from datetime import datetime
from psycopg2 import extras
import numpy as np
import pandas as pd
import os
import psycopg2
import requests
import sys

# Section 1 - Pull player data from app database
# Update tables in database
conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
    os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
    os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

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
new_players['player_id'] = new_players['player_id'].astype('int')
new_players['goals_scored'] = new_players['goals_scored'].astype('int')
new_players.sort_values(by=['player_id'])
new_players.sort_index(inplace=True)

# Write data to file as record
NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
FILE = 'data/update_goals/goals_{}.csv'.format(NOW)
new_players.to_csv(FILE, encoding='utf-8', index=False)


# Section 3 - Compare existing goal scorers data to updated data and store
# new goal scorer timestamps in app database
joint_scorers = pd.merge(players, new_players, on='player_id')
goal_diff = joint_scorers['goals_scored_x'] != joint_scorers['goals_scored_y']
new_scorers = joint_scorers[goal_diff]

# Only need id, first name, and last name of goal scorers
gs_col_names = ['player_id', 'first_name_x', 'second_name_x']
gs_table_cols = ('player_id', 'first_name', 'second_name')
new_scorers = new_scorers[gs_col_names]

# Write goal scored to file as record
gs_NOW = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
gs_FILE = 'data/update_goal_scored/goal_scored_{}.csv'.format(gs_NOW)
new_scorers.to_csv(gs_FILE, encoding='utf-8', index=False)

conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
    os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
    os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

cur = conn.cursor()

with open(gs_FILE, 'r', encoding='utf-8') as row:
    next(row)  # Skip header row
    cur.copy_from(row, 'app.goal_scored', sep=',', columns=gs_table_cols)

conn.commit()

cur.close()
conn.close()


# Section 4 - Update total goals scored by players in app database
# Get totals goals scored for players with an updated amount
updated_goals = joint_scorers[goal_diff][['player_id', 'goals_scored_y']]
updated_goals_l = []
for row in updated_goals.itertuples(index=True):
    updated_goals_l.append((getattr(row, 'player_id'),
                            getattr(row, 'goals_scored_y')))
# Data is in the format [(id_1, updated_goals_1), (id_2, updated_goals_2), ...]

# Create connection to database
conn = psycopg2.connect("dbname={} user={} password={} host={}".format(
    os.environ['f2t_pg_db'], os.environ['f2t_pg_user'],
    os.environ['f2t_pg_pw'], os.environ['f2t_pg_host']))

cur = conn.cursor()

update_player_goals_sql = """
    UPDATE app.player AS p
       SET goals_scored = new.goals_scored_y
       FROM (VALUES %s) AS new(player_id, goals_scored_y)
       WHERE p.player_id = new.player_id
"""
# Update goals scored in player table in app database
psycopg2.extras.execute_values(
    cur, update_player_goals_sql,
    updated_goals_l,
    template=None, page_size=100
)

conn.commit()
cur.close()
conn.close()
