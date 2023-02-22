import pandas as pd

def find_missing(lst):
    return [i for x, y in zip(lst, lst[1:])
        for i in range(x + 1, y) if y - x > 1]
 
# Driver code
df = pd.read_csv('verified/instances.csv')
df = df['game_id'].array
print(find_missing(df))