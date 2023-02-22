import pandas as pd

df = pd.read_csv('verified/instances.csv')
df = df[['game_id', 'crash']]

df['game_id'] = df['game_id'].astype(int)
df = df.drop_duplicates(subset=['game_id'])
df = df.sort_values(by='game_id')
df = df.dropna(subset=['crash'])
df = df.set_index('game_id', drop=True)

# save in a csv file
df.to_csv('verified/instances.csv')