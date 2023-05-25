import csv
import json
import boto3
import urllib.request

def lambda_handler(event, context):
    # Read JSON data from API endpoint
    url = "https://bmx68z5cl1.execute-api.ap-south-1.amazonaws.com/v1/lambda"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    # Perform analysis on data
    goals_by_team = {}
    home_wins = {}
    away_wins = {}
    for game in data:
        home_team = game['Home_Team']
        away_team = game['Away_Team']
        home_goals = int(game['home_team_goal'])
        away_goals = int(game['away_team_goal'])

        # Calculate goals scored by each team
        goals_by_team.setdefault(home_team, [0, 0])[0] += home_goals
        goals_by_team.setdefault(home_team, [0, 0])[1] += 1
        goals_by_team.setdefault(away_team, [0, 0])[0] += away_goals
        goals_by_team.setdefault(away_team, [0, 0])[1] += 1

        # Calculate home and away wins
        if home_goals > away_goals:
            home_wins.setdefault(home_team, 0)
            home_wins[home_team] += 1
            away_wins.setdefault(away_team, 0)
        elif away_goals > home_goals:
            away_wins.setdefault(away_team, 0)
            away_wins[away_team] += 1
            home_wins.setdefault(home_team, 0)
        else:
            away_wins.setdefault(away_team, 0)
            home_wins.setdefault(home_team, 0)

    # Calculate number of wins in 2022 and 2023 for each team
    wins_by_year = {}
    for team in goals_by_team.keys():
        wins_by_year[team] = [0, 0]
    for game in data:
        home_team = game['Home_Team']
        away_team = game['Away_Team']
        home_goals = int(game['home_team_goal'])
        away_goals = int(game['away_team_goal'])
        game_date = game['Date']

        if home_goals > away_goals:
            if game_date.endswith('2022'):
                wins_by_year[home_team][0] += 1
            elif game_date.endswith('2023'):
                wins_by_year[home_team][1] += 1
        elif away_goals > home_goals:
            if game_date.endswith('2022'):
                wins_by_year[away_team][0] += 1
            elif game_date.endswith('2023'):
                wins_by_year[away_team][1] += 1

    # Store analysis results in S3 bucket as CSV
    s3 = boto3.resource('s3')
    bucket_name = 'bucket-selenium-crawler-result'
    bucket = s3.Bucket(bucket_name)
    key = 'goals_wins_by_team.csv'

    # Convert dictionary to CSV formatted string
    csv_str = 'Team,Goals,Matches,Home_Wins,Away_Wins,Wins_2022,Wins_2023\n'
    for team, stats in goals_by_team.items():
        goals = stats[0]
        matches = stats[1]
        home_wins_count = home_wins.get(team, 0)
        away_wins_count = away_wins.get(team, 0)
        wins_2022 = wins_by_year[team][0]
        wins_2023 = wins_by_year[team][1]
        csv_str += f'{team},{goals},{matches},{home_wins_count},{away_wins_count}, {wins_2022}, {wins_2023}\n'

    # Store CSV file in S3 bucket
    bucket.put_object(Key=key, Body=csv_str)
    
    return {
        'statusCode': 200,
        'body': 'Data stored in S3 bucket'
    }
