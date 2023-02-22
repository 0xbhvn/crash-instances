# wip

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as E
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd

# progress bar for the loop
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome()
    return driver

def get_latest_game():
    driver = init_driver()
    url = 'https://bc.game/game/crash'
    driver.get(url)

    WebDriverWait(driver, 10).until(E.presence_of_element_located((By.CLASS_NAME, 'tabs-navs')))

    tabs = driver.find_element(By.CLASS_NAME, 'tabs-navs')
    history_button = tabs.find_element(By.XPATH, 'button[2]')

    WebDriverWait(driver, 10).until(E.element_to_be_clickable((By.CLASS_NAME, 'tabs-nav')))

    history_button.click()

    WebDriverWait(driver, 10).until(E.presence_of_element_located((By.CLASS_NAME, 'ui-table')))

    history_table = driver.find_element(By.XPATH, '//*[@id="root"]/div[3]/div[4]/div[1]/div[3]/div/div[2]/div/div[2]/table/tbody')
    latest_game = history_table.find_element(By.XPATH, 'tr[1]')
    latest_game_id = latest_game.find_element(By.XPATH, 'td[1]').text
    latest_game_seed = latest_game.find_element(By.XPATH, 'td[3]').text

    driver.quit()

    return latest_game_id, latest_game_seed


def get_already_verified_games():
    instances = pd.read_csv('instances.csv')
    instances = instances[['game_id', 'crash']]
    return instances

def verify(latest_game_id, latest_game_seed, instances):
    last_game_id = instances.iloc[[0, -1]]

    driver = init_driver()
    url = 'https://bcgame-project.github.io/verify/crash.html?hash={}&v='.format(latest_game_seed)
    driver.get(url)

    # calculate the number of games to verify
    game_instances = latest_game_id - last_game_id

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

    # end webdriver program
    driver.quit()

    return game_verify_table_rows


def to_csv(latest_game_id, last_game_id, game_verify_table_rows, instances):

    # calculate the number of games to verify
    game_instances = latest_game_id - last_game_id

    id = latest_game_id
    count = 0

    # loop through all verified games
    for row in game_verify_table_rows:

        # end game    
        if id == last_game_id:
            break

        data = row.find_elements(By.TAG_NAME, 'td')

        # get game_id, hash and crash
        instances.loc[len(instances.index)] = [int(id), float(data[1].text)] 

        # progress bar
        progress(count, game_instances)

        # next game
        id -= 1
        count += 1

    instances['game_id'] = instances['game_id'].astype(int)
    instances = instances.drop_duplicates(subset=['game_id'])
    instances = instances.sort_values(by='game_id')
    instances = instances.dropna(subset=['crash'])
    instances = instances.set_index('game_id', drop=True)

    # save in a csv file
    instances.to_csv('instances.csv'.format(latest_game_id))

latest_game_id, latest_game_seed = get_latest_game()
instances = get_already_verified_games()
game_verify_table_rows = verify(latest_game_id, latest_game_seed, instances)
to_csv(latest_game_id, latest_game_seed, game_verify_table_rows, instances)