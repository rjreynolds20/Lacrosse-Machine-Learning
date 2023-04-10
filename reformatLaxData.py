import pandas as pd
import numpy as np
import math

# Want to read in CSV file.
# Want to create a CSV file with all A - B games, and another with the B - A games.
# One row should have all of A's features followed by all of B's features followed by Home Win, Neutral Win, Away Win
# Want to remove goals/goals against at a future time.

# Remove Goals, Goals Against, Games w/o duplicates.
# Want an outside loop to go through each row.
# Want a check to make sure that the dates are the same.
# Want another check to make sure that you're getting the opponents game data.


# Gathers team's data while ignoring specific features for reformat.
def gatherTeamData(df, row, status):
    rowData = []
    flag = False

    for i in range(0, 30, 1):
        # Opponent Name, Score, Goals, Face offs taken, GMin, Goals allowed, HeadCoach, Location
        # Might want GMin later.
        if (status == 2):
            # Removes date, home/away/neutral, OT attributes from second input.
            if (i == 1 or i == 6):
                continue
            elif (i == 3):
                if (df[row][i + 1] < df[row][i + 2]):
                    teamWin = 1
                else:
                    teamWin = -1
                continue
            elif (i == 21):
                gameTime = df[row][i]
                continue
        if (i == 2 or i == 4 or i == 5 or i == 7 or i == 18 or i == 21 or i == 22 or i == 27 or i == 29): #3 4 5 21 27
            continue
        elif (i == 3 and status == 1):
            if (df[row][i] == 'HOME'):
                han = 1
            elif (df[row][i] == 'NEUTRAL'):
                han = 0
            else:
                han = -1
            rowData.append(han)
            continue
        else:
            rowData.append(df[row][i])
    if (status == 2 and  flag == False):
        rowData.append(3600 - gameTime)
        rowData.append(teamWin)
    elif (flag == True):
        rowData = []
    return rowData


# Reformats data as desired for sports machine learning.
def bruteForceReformat(df):
    data = []
    rowData = []
    flag = False

    for row in range(0, len(df), 1):
        # Skips over cancelled games.
        if (math.isnan(df[row][4])):
            continue
        else:
            rowData.extend(gatherTeamData(df, row, 1))
        # Have to start at zero to get the duplicate games for testing purposes. ---> very inefficient
        for newRow in range(0, len(df), 1):
            # If date is the same and team name is the same as opponent name.
            if ((df[row][1] == df[newRow][1]) and (df[row][0] == df[newRow][2])):
                rowData.extend(gatherTeamData(df, newRow, 2))
                flag = False
                break
            # If a game doesn't have a duplicate.
            else:
                flag = True
        # Ignores games that do not have duplicates --> does not add to new CSV.
        if (flag == True):
            rowData = []
            continue
        data.append(rowData)
        rowData = []

    return data


######################################################################################################################

# Non-Duplicate Deletion & Sorting Data

######################################################################################################################

# 18-21 34-40

def searchDuplicate(df, teamName, opponentName, teamWin, currRow):
    count = 0
    for i in range(0, len(df), 1):
        if (df[i][0] == opponentName and df[i][1] == df[currRow][1] and df[i][18] == teamName and df[i][34] != teamWin):
            count += 1
    if (count > 1 or count < 1):
        return False
    return True


def separateData(df):
    data = []
    for row in range(0, len(df), 1):
        if (searchDuplicate(df, df[row][0], df[row][18], df[row][34], row) == True):
            data.append(df[row])
    return data


######################################################################################################################

# Removing specific characters

######################################################################################################################


def removeCommas(df): #15, 33, 39
    data = []
    for row in range(0, len(df), 1):
        if (df[row][15].find(',') != -1):
            fixed = df[row][15].replace(',', '')
            data.append(fixed)
            continue
        if (df[row][33].find(',') != -1):
            fixed = df[row][33].replace(',', '')
            data.append(fixed)
            continue
        if (df[row][39].find(',') != -1):
            fixed = df[row][39].replace(',', '')
            data.append(fixed)
            continue
        data.append(df[row])
    return data

######################################################################################################################

# Calling Section - Below!

######################################################################################################################

df = pd.read_csv('Training Data\Clearing Data\Training Data - Clearing.csv', low_memory=False) #nrows = 
#df = pd.read_csv('REMOVEDNONDUPLICATES.csv', low_memory=False)
laxdata = df.values
# Removed new heach coach column for now.
#headers = ['Team', 'Date', 'Home/Neutral/Away', 'OT', 'Assists', 'Points', 'Shots', 'SOG', 'Man-Up G', 
#            'Man-Down G', 'GB', 'TO', 'CT', 'FO Won', 'Pen', 'Pen Time', 'Saves', 'Clears', 'Clear Att', 
#            'Clear Pct', 'Roster Size',
#
#            'Opponent', 'OAssists', 'OPoints', 'OShots', 'OSOG', 'OMan-Up G', 'OMan-Down G', 'OGB', 'OTO', 'OCT', 
#            'OFO Won', 'OPen', 'OPen Time', 'OSaves', 'OClears', 'OClear Att', 'OClear Pct', 'ORoster Size', 'GameTime Difference', 'Team Win']
headers = ['Team', 'Date', 'Home/Neutral/Away', 'OT', 'Assists', 'Points', 'Shots', 'SOG', 'Man-Up G', 
            'Man-Down G', 'GB', 'TO', 'CT', 'FO Won', 'Pen', 'Pen Time', 'Saves', 'Roster Size',

            'Opponent', 'OAssists', 'OPoints', 'OShots', 'OSOG', 'OMan-Up G', 'OMan-Down G', 'OGB', 'OTO', 'OCT', 
            'OFO Won', 'OPen', 'OPen Time', 'OSaves', 'ORoster Size', 'GameTime Difference', 'Team Win']
#csvData = separateData(laxdata)
csvData = removeCommas(df)
data = pd.DataFrame(csvData, columns=headers)
data.to_csv("TEMP.csv", index=False)

# Want to gather win data and new head coach feature.
# Error with the games that were cancelled <--- show up as loss for both teams.