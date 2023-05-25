from selenium import webdriver
import pandas as pd
import boto3
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
from io import StringIO

s3_client = boto3.client('s3')

options = webdriver.ChromeOptions()
options.add_argument("--headless") # to run Chrome in headless mode
options.add_argument("--window-size=1920,1200")
options.add_experimental_option("excludeSwitches", ["enable-automation"])  
options.add_experimental_option("useAutomationExtension", False)

website = 'https://www.adamchoi.co.uk/overs/detailed'
driver = webdriver.Chrome(options = options)
driver.get(website)

all_matches_button = driver.find_element_by_xpath('//label[@analytics-event="All matches"]')
all_matches_button.click()

# Define a dictionary of countries and their available leagues
country_leagues = {
    'England': ['Premier League', 'Championship', 'League One', 'League Two', 'National League'],
    'Spain': ['La Liga', 'Segunda Division'],
    'Germany': ['Bundesliga', 'Bundesliga 2'],
    'Italy': ['Serie A', 'Serie B'],
    'France': ['Ligue 1', 'Ligue 2'],
    'Scotland': ['SPL', 'Scottish Championship', 'Scottish League 1', 'Scottish League 2'],
    'Netherlands': ['Eredivisie', 'Eerste Divisie'],
    'Portugal': ['Portuguese Liga NOS'],
    'Turkey': ['Turkish Super Lig'],
    'Greece': ['Greek Super League'],
    'Belgium': ['Pro League', 'First Division B'],
    'Austria': ['Bundesliga'],
    'Russia': ['Premier League'],
    'Denmark': ['Superliga'],
    'Poland': ['Ekstraklasa'],
}


for country, leagues in country_leagues.items():
    for league in leagues:
        #select the country
        dropdown = Select(driver.find_element_by_id('country'))
        dropdown.select_by_visible_text(country)
        time.sleep(3)

        #select the league
        dropdown = Select(driver.find_element_by_id('league'))
        dropdown.select_by_visible_text(league)
        time.sleep(3)

        #Select the season
        dropdown = Select(driver.find_element_by_id('season'))
        dropdown.select_by_visible_text('22/23')
        time.sleep(5)

        matches = driver.find_elements_by_tag_name('tr')

        date = []
        home_team = []
        score = []
        away_team = []

        for match in matches:
            date.append(match.find_element_by_xpath('./td[1]').text)
            home_team.append(match.find_element_by_xpath('./td[2]').text)
            score.append(match.find_element_by_xpath('./td[3]').text)
            away_team.append(match.find_element_by_xpath('./td[4]').text)
            
        df = pd.DataFrame({'Country':country, 'League':league, 'Date': date, 'Home_Team': home_team, 'Score': score, 'Away_Team': away_team})
        df[['home_team_goal', 'away_team_goal']] = df['Score'].str.split(' - ', expand=True)
        df.drop('Score', axis=1, inplace=True)
        df = df.reindex(columns=['Country', 'League', 'Date', 'Home_Team', 'home_team_goal', 'away_team_goal', 'Away_Team'])
        # drop rows with "?" symbol
        df = df[(df['home_team_goal'] != '?') & (df['away_team_goal'] != '?')]
        
        
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        df = df[(df['Date'].dt.year == current_year) & (df['Date'].dt.month.isin([current_month, current_month - 1]))]



        # Get the current timestamp in a specific format
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'{country}_{league}_{timestamp}.csv'
        
        abc = StringIO()
        
        df.to_csv(abc, index=False)
        abc.seek(0)
        s3_client.put_object(Bucket='bucket-selenium-crawler', Body=abc.getvalue(), Key=filename)
driver.quit()