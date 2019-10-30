"""
This script pulls a data dump from the Fantasy.PremierLeague.com site, extracts
the id and first and last name of each football player, and outputs the data to
a CSV file.
"""
import numpy as np
import pandas as pd
import requests


# Pull data from Fantasy.PremierLeague.com
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
response = requests.get(url)
elements = response.json()['elements']

# Extract player id and first and last name to a DataFrame
df = pd.DataFrame(np.empty((len(elements), 3)))
df[:] = np.nan
df.columns = ['id', 'first_name', 'last_name']

for i in range(len(elements)):
    df.iloc[i, 0] = str(elements[i]['id'])
    df.iloc[i, 1] = str(elements[i]['first_name'])
    df.iloc[i, 2] = str(elements[i]['second_name'])

df.to_csv('data/player_data.csv', encoding='utf-8', index=False)
