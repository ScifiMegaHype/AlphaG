# https://sqa.stackexchange.com/questions/22191/is-it-possible-to-automate-drag-and-drop-from-a-file-in-system-to-a-website-in-s
# Latest stable release of ChromeDriver: https://chromedriver.chromium.org/, https://googlechromelabs.github.io/chrome-for-testing/

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import sys
from subprocess import CREATE_NO_WINDOW
from time import sleep

def resource_path(relative_path) -> str:
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def setupDriver() -> webdriver:
    # Options
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    options = webdriver.ChromeOptions()
    options.binary_location = 'chromeassets/chrome.exe'
    # options.add_argument("--headless=new") # runs driver in background
    options.add_experimental_option("prefs",prefs)

    # Service
    chrome_service = ChromeService(resource_path('chromeassets/chromedriver.exe'))
    chrome_service.creation_flags = CREATE_NO_WINDOW
    
    # Driver
    driver = webdriver.Chrome(service=chrome_service, options=options) 
    driver.set_window_size(920,700)

    return driver

def acceptCookies(driver: webdriver) -> None:
    try:
        accept_cookies_button = driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
        close_button = driver.find_element(By.XPATH, "//a[@class='closeBtn']")
        
        accept_cookies_button.click()
        close_button.click()

    except Exception as e:
        print(e)
    
    sleep(2) # Give the page enough time to reload after accepting cookies,
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.CONTROL + Keys.END)

    return 

def rankingSeeker() -> list:
    print('Loading...')
    driver = setupDriver()
    driver.get(f"https://en.wikipedia.org/wiki/2024%E2%80%9325_UEFA_Champions_League_league_phase#Matchday_1")

    pot_tables = driver.find_elements(By.XPATH, ".//table")[2:6] 
    teams_list = []
    for table in pot_tables:
        for line_num, line in enumerate(table.text.split('\n')):
            if line_num>1: teams_list.append(sanitize_team_name(line))
    
    return teams_list

def rankingSeekerPL() -> list:
    print('Loading...')
    driver = setupDriver()
    driver.get(f"https://www.premierleague.com/tables?co=1&se=719&ha=-1")
    acceptCookies(driver)

    table = driver.find_elements(By.XPATH, \
                    ".//span[@class='league-table__team-name league-table__team-name--short short']")[0:20]
    
    teams_list = [table_row.get_attribute("innerText") for table_row in table]
    
    return teams_list

def goalSeeker() -> list:
    driver = setupDriver()
    driver.get(f"https://en.wikipedia.org/wiki/2024%E2%80%9325_UEFA_Champions_League_league_phase#Matchday_1")

    a_ref = driver.find_elements(By.XPATH, "//div[@class='footballbox']")

    scorers = []
    goals_list = []
    for item in a_ref: 
        team_names =  item.get_attribute('id')
        table = item.find_elements(By.XPATH, ".//table")[0] # first table
        home_goals_list = table.find_element(By.XPATH, ".//td[@class='fhgoal']").find_elements(By.TAG_NAME, 'li')
        away_goals_list = table.find_element(By.XPATH, ".//td[@class='fagoal']").find_elements(By.TAG_NAME, 'li')

        number_of_goals_scored_by_home_team = 0
        for every_goal_element in home_goals_list:
            scorer_goals_elements = every_goal_element.find_elements(By.XPATH, ".//span[@class='fb-goal']/span")
            number_of_goals_scored_by_home_team += len(scorer_goals_elements)-1

        number_of_goals_scored_by_away_team = 0
        for every_goal_element in away_goals_list:
            scorer_goals_elements = every_goal_element.find_elements(By.XPATH, ".//span[@class='fb-goal']/span")
            number_of_goals_scored_by_away_team += len(scorer_goals_elements)-1

        # number_of_goals = number_of_goals_scored_by_home_team+number_of_goals_scored_by_away_team
        print(f'{team_names} {number_of_goals_scored_by_home_team}:{number_of_goals_scored_by_away_team}')
        with open('log.txt', 'a') as f:
            f.write(f'{team_names} {number_of_goals_scored_by_home_team}:{number_of_goals_scored_by_away_team}\n')

        goals_elements = [home_goals_list, away_goals_list]
        for index, home_away_goal_element in enumerate(goals_elements):
            for every_goal_element in home_away_goal_element:
                if index==0: 
                    team = team_names.split('_v_')[0].replace('_', ' ')
                    opponent = team_names.split('_v_')[1].replace('_', ' ')
                    team_goal_count = number_of_goals_scored_by_home_team
                    opponent_goal_count = number_of_goals_scored_by_away_team
                elif index==1: 
                    team = team_names.split('_v_')[1].replace('_', ' ')
                    opponent = team_names.split('_v_')[0].replace('_', ' ')
                    team_goal_count = number_of_goals_scored_by_away_team
                    opponent_goal_count = number_of_goals_scored_by_home_team

                scorer_name_element = every_goal_element.find_element(By.TAG_NAME, 'a')
                scorer_name = scorer_name_element.get_attribute('title')
                scorer_goals_elements = every_goal_element.find_elements(By.XPATH, ".//span[@class='fb-goal']/span")
                number_of_goals_scored_by_scorer = len(scorer_goals_elements)-1

                try: 
                    print(f'{scorer_name} ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}')
                    with open('log.txt', 'a') as f:
                        f.write(f'{scorer_name} ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}\n')
                    goals_list.append([scorer_name,number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                    scorers.append(scorer_name)
                except UnicodeEncodeError:
                    try: 
                        print(f'{sanitize_string(scorer_name)} ({number_of_goals_scored_by_scorer}) goal against {opponent}')
                        with open('log.txt', 'a') as f:
                            f.write(f'{sanitize_string(scorer_name)} ({number_of_goals_scored_by_scorer}) goal against {opponent}\n')
                        goals_list.append([sanitize_string(scorer_name),number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                        scorers.append(sanitize_string(scorer_name))
                    except: 
                        print(f'Unknown ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}')     
                        with open('log.txt', 'a') as f:
                            f.write(f'Unknown ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}\n')
                        goals_list.append(['Unkown',number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                        scorers.append('Unkown')
        print('\n')
        with open('log.txt', 'a') as f:
            f.write('\n\n') 

    return goals_list, scorers

def goalSeekerPL() -> list:
    driver = setupDriver()
    
    match_ids = getMatchIds(driver)

    scorers = []
    goals_list = []
    for match_id in match_ids:
        try:
            wait_time = .1
            match_page_data = getGoalsData(driver, wait_time, match_id, goals_list, scorers)
            goals_list = match_page_data[0]
            scorers = match_page_data[1]
        except Exception as e:
            print(f'{match_id} failed:\n{e}')
            with open('log.txt', 'a') as f:
                f.write(f'{match_id} failed:\n{e}\n')

    return goals_list, scorers

def getMatchIds(driver: webdriver) -> list:
    driver.get(f"https://www.premierleague.com/results")
    acceptCookies(driver)
    print("Loading match results data...")
    sleep(10) # Give the page enough time to display all matches after scrolling to the bottom.
    
    match_fixture_divs = driver.find_elements(By.XPATH, "//div[@class='match-fixture__wrapper js-fixture postMatch']")

    return [div.get_attribute('data-matchid') for div in match_fixture_divs]

def getGoalsData(driver: webdriver, wait_time: float, match_id: str|int, goals_list: list, scorers: list): # also capture own goals
    driver.get(f"https://www.premierleague.com/match/{match_id}")
    sleep(wait_time) # Give some time to load the match page
    
    table = driver.find_element(By.XPATH, "//div[@class='mc-summary__teams-container']")
    team_names_elements =  table.find_elements(By.XPATH, ".//div[@class='mc-summary__team-container']")[0:2]
    team_names_list = [
        element.find_element(By.XPATH, \
        ".//div//a[starts-with(@class, 'mc-summary__team')]//span[contains(@class, 'show')]").\
        get_attribute("innerText") for element in team_names_elements
        ]
    team_names = '_v_'.join(team_names_list)

    home_goals_list = table.find_elements(By.XPATH, \
                        ".//div[@class='matchEvents matchEventsContainer home']//div[@class='mc-summary__event']")
    away_goals_list = table.find_elements(By.XPATH, \
                        ".//div[@class='matchEvents matchEventsContainer away']//div[@class='mc-summary__event']")
    
    number_of_goals_scored_by_home_team = 0
    for every_goal_element in home_goals_list:
        scorer_goals_elements = getListOfGoalTimes(every_goal_element)
         
        number_of_goals_scored_by_home_team += len(scorer_goals_elements)

    number_of_goals_scored_by_away_team = 0
    for every_goal_element in away_goals_list:
        scorer_goals_elements = getListOfGoalTimes(every_goal_element)
        number_of_goals_scored_by_away_team += len(scorer_goals_elements)

    # number_of_goals = number_of_goals_scored_by_home_team+number_of_goals_scored_by_away_team
    print(f'{team_names} {number_of_goals_scored_by_home_team}:{number_of_goals_scored_by_away_team}')
    with open('log.txt', 'a') as f:
        f.write(f'{team_names} {number_of_goals_scored_by_home_team}:{number_of_goals_scored_by_away_team}\n')

    goals_elements = [home_goals_list, away_goals_list]
    for index, home_away_goal_element in enumerate(goals_elements):
        for every_goal_element in home_away_goal_element:
            if index==0: 
                team = team_names.split('_v_')[0].replace('_', ' ')
                opponent = team_names.split('_v_')[1].replace('_', ' ')
                team_goal_count = number_of_goals_scored_by_home_team
                opponent_goal_count = number_of_goals_scored_by_away_team
            elif index==1: 
                team = team_names.split('_v_')[1].replace('_', ' ')
                opponent = team_names.split('_v_')[0].replace('_', ' ')
                team_goal_count = number_of_goals_scored_by_away_team
                opponent_goal_count = number_of_goals_scored_by_home_team

            number_of_goals_scored_by_scorer = 0 
            if "og" not in getElementSourceName(every_goal_element):
                scorer_name = getPlayerNameAndSurname(every_goal_element)
                scorer_goals_elements = getListOfGoalTimes(every_goal_element)
                number_of_goals_scored_by_scorer += len(scorer_goals_elements)

                try: 
                    print(f'{scorer_name} ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}')
                    with open('log.txt', 'a') as f:
                        f.write(f'{scorer_name} ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}\n')
                    goals_list.append([scorer_name,number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                    scorers.append(scorer_name)
                except UnicodeEncodeError:
                    try: 
                        print(f'{sanitize_string(scorer_name)} ({number_of_goals_scored_by_scorer}) goal against {opponent}')
                        with open('log.txt', 'a') as f:
                            f.write(f'{sanitize_string(scorer_name)} ({number_of_goals_scored_by_scorer}) goal against {opponent}\n')
                        goals_list.append([sanitize_string(scorer_name),number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                        scorers.append(scorer_name)
                    except: 
                        print(f'Unknown ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}')     
                        with open('log.txt', 'a') as f:
                            f.write(f'Unknown ({number_of_goals_scored_by_scorer}) goal(s) for {team} against {opponent}\n')
                        goals_list.append(['Unkown',number_of_goals_scored_by_scorer, team, opponent, team_goal_count, opponent_goal_count])
                        scorers.append(scorer_name)
            else: 
                scorer_name = getPlayerNameAndSurname(every_goal_element)
                try:
                    print(f'{scorer_name} scored an own goal for {team} against {opponent}')
                    with open('log.txt', 'a') as f:
                        f.write(f'{scorer_name} scored an own goal for {team} against {opponent}\n')
                except UnicodeEncodeError: 
                    print(f'Unknown scored an own goal for {team} against {opponent}')
                    with open('log.txt', 'a') as f:
                        f.write(f'Unkown scored an own goal for {team} against {opponent}\n')

    print('\n')
    with open('log.txt', 'a') as f:
        f.write('\n\n') 

    return goals_list, scorers

def getListOfGoalTimes(goal_element) -> str:
    return goal_element.find_element(By.XPATH, ".//span").get_attribute("innerText").split(',')

def getElementSourceName(every_goal_element):
    return every_goal_element.find_element(By.XPATH, ".//span//img[@class='mc-summary__event-time-icon']").get_attribute("src")

def getPlayerNameAndSurname(every_goal_element) -> str:
    scorer_name_element = every_goal_element.find_element(By.XPATH, ".//div//a[@class='mc-summary__scorer']")
    try:
        scorer_name = scorer_name_element.find_element(By.XPATH, \
                    ".//div[@class='mc-summary__scorer-name-first']").get_attribute("innerText")
    except: # For players with not first name
        scorer_name = ''
    try: 
        scorer_surname = scorer_name_element.find_element(By.XPATH, ".//div[@class='mc-summary__scorer-name-last']").\
        get_attribute("innerText")
    except: # for players with no last name
        scorer_surname = ''
    
    scorer_name_surname = f"{scorer_name} {scorer_surname}".strip()

    return scorer_name_surname

def sanitize_string(string: str) -> str:
    mappings = [
        ['\\xc3\\x87','C'], ['\\xc4\\x8d', 'c'], ['\\xc4\\x87','c'], ['\\xc4\\x9f','g'], ['\\xc4\\xb1','i'],
        ['\\xc4\\xb0','L'], ['\\xc5\\xa0','S'], ['\\xc5\\xa1','s'], ['\\xc3\\xbc','u'], ['\\xc3\\xbc','u'],
        ['\\xc3\\xad','i'], ['\\xc5\\x81','L'], ['\\xc5\\xbe','z'] 
    ]
    string = str(string.encode("utf-8"))
    for map in mappings:
        string = string.replace(map[0], map[1])
    
    return string.replace("b\'", '').replace("\'",'')

def sanitize_team_name(line: str) -> str:
    remove = line.split(' ')[-1]
    line = line.replace(remove,'')
    
    removal_list = ['[TH]', '[EL]','[CP]', '[LP]']
    for removal in removal_list: 
        line = line.replace(removal,'')
    
    return line.strip()