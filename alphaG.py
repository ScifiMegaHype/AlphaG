# https://en.wikipedia.org/wiki/2024%E2%80%9325_UEFA_Champions_League_league_phase#Matchday_1
# https://www.premierleague.com/tables?co=1&se=719&ha=-1
# https://www.premierleague.com/results
# https://www.premierleague.com/match/{match_id}

from mylibs.wikiscrape import rankingSeeker, goalSeeker, rankingSeekerPL, goalSeekerPL 
from mylibs.goal import Goal
import pandas as pd
from openpyxl import load_workbook
import cProfile
import pstats

def wipeLogFile() -> None:
    with open('log.txt', 'w') as f:
        f.write('')

def setup_goals_elements_list(teams_ranking_list, goals_list) -> list:
    goals = []
    for goal in goals_list:
        goal_scorer = goal[0]
        number_of_goals = goal[1]
        goal_for, goal_against = goal[2], goal[3]
        team_goal_count, opponent_goal_count = goal[4], goal[5]

        goal_for_rank = teams_ranking_list.index(goal_for)+1
        goal_against_rank = teams_ranking_list.index(goal_against)+1

        goals.append(Goal(goal_scorer, number_of_goals, goal_for_rank, goal_against_rank, team_goal_count, opponent_goal_count, len(teams_ranking_list)))

    return goals

def getPlayerGoalsAndAlphaG(goals: list, focus_player: str, teams_ranking_list: list):
    total_alphaG = 0.0
    total_scorer_goals = 0
    for goal in goals:
        if goal.scorer==focus_player:
            total_scorer_goals += goal.number_of_goals
            alphaG = goal.alphaGv2()
            total_alphaG += alphaG
            print(f'{alphaG} against {teams_ranking_list[goal.opponent_ranking-1]}') 
            with open('log.txt', 'a') as f:
                f.write(f'{alphaG} against {teams_ranking_list[goal.opponent_ranking-1]}\n')

    return total_scorer_goals, total_alphaG

def createExcelAnalysisFile(unique_scorers: set, total_scorer_goals_column_list: list, total_alphaG_column_list: list, excel_file_name: str) -> None:
    # dictionary with list object in values
    details = {
        'Scorer' : list(unique_scorers),
        'Goals Scored' : total_scorer_goals_column_list,
        'Total AlphaG' : total_alphaG_column_list,
    }
    
    # creating a Dataframe object 
    df = pd.DataFrame(details)

    # sending dataframe to excel
    df.to_excel(excel_file_name, index=False)

    # adjust cell sizes 
    adjust_cell_size(excel_file_name)

def adjust_cell_size(file_path: str):
    wb = load_workbook(file_path)  

    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter 
            for cell in col:
                try: 
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column].width = adjusted_width

    wb.save(file_path)
    wb.close()

def main(competition: str) -> None:
    if  competition.lower()=='cl':
        teams_ranking_list = rankingSeeker()
        goals_list, scorers = goalSeeker()
    elif  competition.lower()=='pl':
        teams_ranking_list = rankingSeekerPL()
        goals_list, scorers = goalSeekerPL()
    else:
        print("Invalid competition: Supported competition are only cl and pl")
        with open('log.txt', 'w') as f:
            f.write('Invalid competition: Supported competition are only cl and pl')
        return
    
    goals = setup_goals_elements_list(teams_ranking_list, goals_list) 

    unique_scorers = set(scorers)
    total_alphaG_column_list = []
    total_scorer_goals_column_list = []

    for unique_scorer in unique_scorers:
        # alphaG calculation
        total_scorer_goals, total_alphaG = getPlayerGoalsAndAlphaG(goals, unique_scorer, teams_ranking_list) 
        total_scorer_goals_column_list.append(total_scorer_goals)
        total_alphaG_column_list.append(round(total_alphaG, 2))

        print(f'{unique_scorer}\'s total_alphaG is {total_alphaG:.2f} with {total_scorer_goals} goals')
        print('')
        with open('log.txt', 'a') as f:
            f.write(f'{unique_scorer}\'s total_alphaG is {total_alphaG:.2f} with {total_scorer_goals} goals\n\n')

    createExcelAnalysisFile(unique_scorers, total_scorer_goals_column_list, total_alphaG_column_list, excel_file_name)

    print('Done')

if __name__ == '__main__':
    with cProfile.Profile() as profile:
        wipeLogFile()

        competition = 'pl' # pl or cl
        excel_file_name = f'AlphaG Analysis {competition.upper()}.xlsx'

        main(competition)

    results = pstats.Stats(profile)
    results.sort_stats(pstats.SortKey.TIME)
    results.dump_stats('profile.profile') # python -m tuna profile.profile