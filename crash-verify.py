# to run: python3 crash-verify.py

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as E
import pandas as pd

# progress bar for the loop
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

# read csv file and create dataframe
df = pd.read_csv('verified/instances.csv')
df = df[['game_id', 'crash']]

# get the last verified game_id
last_verified_game_id = int(df["game_id"].iloc[-1])

# constants
game_id = int(input('game_id: '))
game_seed = input('game_seed: ')

# calculate the number of games to verify
game_instances = game_id - last_verified_game_id
print('fetching latest {} instances'.format(game_instances))

# webdriver program
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

url = 'https://bcgame-project.github.io/verify/crash.html?hash={}&v='.format(game_seed)
driver.get(url)

# verify games
game_amount_input = driver.find_element(By.XPATH, '//*[@id="game_amount_input"]')
game_amount_input.clear()
game_amount_input.send_keys(game_instances)

game_verify_submit = driver.find_element(By.XPATH, '//*[@id="game_verify_submit"]')
game_verify_submit.click()

WebDriverWait(driver, 10).until(E.presence_of_element_located((By.CLASS_NAME, 'is-loading')))

while game_verify_submit.get_attribute('disabled'):
    pass

# get all verified games
game_verify_table = driver.find_element(By.XPATH, '//*[@id="game_verify_table"]')
game_verify_table_rows = game_verify_table.find_elements(By.TAG_NAME, 'tr')

id = game_id
count = 0

# loop through all verified games
for row in game_verify_table_rows:
    # end game    
    if id == last_verified_game_id:
        break

    data = row.find_elements(By.TAG_NAME, 'td')

    # get game_id, hash and crash
    df.loc[len(df.index)] = [int(id), float(data[1].text)] 

    # progress bar
    progress(count, game_instances)

    # next game
    id -= 1
    count += 1

df['game_id'] = df['game_id'].astype(int)
df = df.drop_duplicates(subset=['game_id'])
df = df.sort_values(by='game_id')
df = df.dropna(subset=['crash'])
df = df.set_index('game_id', drop=True)

# save in a csv file
df.to_csv('verified/instances.csv')

# end webdriver program

driver.quit()

# after dip, when is the next 30x/40x/50x/60x/70x/80x/90x/100x?