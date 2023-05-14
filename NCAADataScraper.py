from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException 
import time


# *************************************************** #

# FUNCTION SECTION

# *************************************************** #

def checkPath(driver, path, type):
    if (type == 'XPATH'):
        try:
            driver.find_element(By.XPATH, path)
        except NoSuchElementException:
            return False
        return True
    elif (type == 'CSS'):
        try:
            driver.find_element(By.CSS_SELECTOR, path)
        except NoSuchElementException:
            return False
        return True


# Function launches chrome and defaults to NCAA website.
def launchBrowser(path):
    chrome_options = Options()
    chrome_options.binary_location="../Google Chrome"
    chrome_options.add_argument("start-maximized")
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    driver.implicitly_wait(10)
    driver.get(path)
    return driver


# Function gathers headers for the DF.
def gatherHeaders(path):
    driver = launchBrowser("http://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=15921&org_id=578&stats_player_seq=-100")
    data = ['Team']
    basket = driver.find_elements(By.XPATH, path)

    num = 0
    for item in basket:
        if (num == 2):
            data.append('Home/Away')
            data.append('Team Score')
            num += 1
            continue
        elif (num == 3):
            data.append('Opponent Score')
            data.append('OT')
            num += 1
            continue
        elif (num == 21 or num == 22 or num == 23 or num == 24 or num == 25):
            num += 1
            continue
        data.append(item.text)
        num += 1
    driver.close()
    return data


# Function gathers an array of team names.
def gatherTeamNames():
    driver = launchBrowser("http://stats.ncaa.org/rankings/ranking_summary")
    teams = []
    selectSport = driver.find_element(By.CSS_SELECTOR, '#sport')
    selectSport.click()
    sport = driver.find_element(By.XPATH, '/html/body/div[2]/select[1]/option[6]')
    sport.click()
    selectDivision = driver.find_element(By.CSS_SELECTOR, '#u_div')
    selectDivision.click()
    division = driver.find_element(By.XPATH, '/html/body/div[2]/select[3]/option[2]')
    division.click()
    dropDown = driver.find_element(By.CSS_SELECTOR, '#ranking_summary_form_org_id')
    divisionTeams = Select(dropDown)
    for team in divisionTeams.options:
        teams += [team.text]
    del teams[0]
    for i in range(2, 4):
        division = driver.find_element(By.XPATH, '/html/body/div[2]/select[3]/option['+str(i)+']')
        division.click()
        dropDown = driver.find_element(By.CSS_SELECTOR, '#ranking_summary_form_org_id')
        divisionTeams = Select(dropDown)
        for team in divisionTeams.options:
            if (team.text == 'Select Team'):
                continue
            teams += [team.text]
    driver.close()
    return teams


# Function takes a given team and a season number and returns the season data
#          from that given input.
def gatherSeasonData(table, teamName, seasonNo):
    data = []
    rows = table.find_elements(By.CSS_SELECTOR, 'tr')

    # Num to get specific rows because there are empty rows included
    num = 3
    # Flag for postponed games
    flag = False
    # Tracks number of cancelled games in case there are more than one.
    cancelledGames = 1
    for row in rows:
        if ((flag == False and num % 2 > 0) or (flag == True and num % 2 == 0)):
        # Number of columns
            gameData = [teamName]

            featureNum = 0
            features = table.find_elements(By.XPATH, 'tbody/tr['+str(num)+']/td')
            for feature in features:
                # Turns dates into strings
                if (featureNum == 0):
                    gameData.append(str(feature.text))
                    featureNum += 1
                    continue

                # Fills HOME/AWAY Column of gameData
                elif (featureNum == 1):
                    if (feature.text.find('@') == -1):
                        gameData.append(feature.text)
                        gameData.append('HOME')
                    else:
                        if (feature.text[0] == '@'):
                            opponentName = feature.text.split(' ', 1)
                            gameData.append(opponentName[1])
                            gameData.append('AWAY')
                        else:
                            opponentName = feature.text.split('@', 1)
                            gameData.append(opponentName[0].strip())
                            gameData.append('NEUTRAL')
                    featureNum += 1
                    continue

                # Result(2) now turns into Team Score, Opponent Score, and OT (0/1)
                elif (featureNum == 2):
                    # Postponed games need flag and counter to track.
                    if (feature.text == '-' or (seasonNo >= 4 and (feature.text.find('W') == -1 and feature.text.find('L') == -1))):
                        if (cancelledGames % 2 > 0):
                            flag = True
                            cancelledGames += 1
                            break
                        elif (cancelledGames % 2 == 0):
                            flag = False
                            cancelledGames += 1
                            break
                    
                    # Fixes score string up to be parsed into array appropriately.
                    fixedScore = feature.text.replace('W', '')
                    fixedScore = fixedScore.replace('L', '')
                    fixedScore = fixedScore.replace(' ', '')

                    if (fixedScore.find('(') != -1):
                        otSplit = fixedScore.split("(", 1)
                        score = otSplit[0].split("-", 1)
                    else:
                        score = fixedScore.split("-", 1)
                    gameData.append(score[0])
                    gameData.append(score[1])

                    # Checks for OT feature and parses appropriately.
                    if (fixedScore.find('(') == -1):
                        gameData.append(0)
                    else:
                        gameData.append(1)

                    featureNum += 1
                    continue

                # Changes null to zero for goals, assists, points, shots, SOG, man down G, man up G, turnovers, faceoffs won, goals against, saves, # of penalties, penalty time.
                elif ((seasonNo < 5 and (featureNum == 4 or featureNum == 5 or featureNum == 6 or featureNum == 7 or featureNum == 8 or 
                     featureNum == 9 or featureNum == 10 or featureNum == 13 or featureNum == 14 or featureNum == 16 or featureNum == 17 or featureNum == 19 or featureNum == 20)) 
                     or seasonNo >= 5 and (featureNum == 3 or featureNum == 4 or featureNum == 5 or featureNum == 6 or featureNum == 7 or featureNum == 8 or
                     featureNum == 9 or featureNum == 12 or featureNum == 13 or featureNum == 15 or featureNum == 16 or featureNum == 18 or featureNum == 19)):
                    if (feature.text == ''):
                        gameData.append(0)
                        featureNum += 1
                        continue

                # Fixes game time total from minutes to whole number seconds.
                elif ((seasonNo <= 4 and featureNum == 18) or (seasonNo >= 5 and featureNum == 17)):
                    if (feature.text == ''):
                        gameData.append(0)
                        featureNum += 1
                        continue
                    gameTime = feature.text.replace('*', '')
                    gameTime = gameTime.replace('/', '')
                    if (gameTime.find(':') != -1):
                        gameTime = gameTime.split(':', 1)
                        hours = int(gameTime[0])
                        seconds = int(gameTime[1])
                        time = (hours * 60) + seconds
                        gameData.append(time)
                        featureNum += 1
                        continue
                    else:
                        gameTime = gameTime.replace(',', '')
                        gameData.append(gameTime)
                        featureNum += 1
                        continue

                # 2016-17 removes 'G' column, 2013-14 removes 'OTG', 2013-14 onward removes clearing data
                elif ((seasonNo < 5 and (featureNum == 3 or featureNum == 21 or featureNum == 22 or featureNum == 23 or featureNum == 24 or featureNum == 25)) 
                or (seasonNo >= 5 and (featureNum == 20 or featureNum == 21 or featureNum == 22 or featureNum == 23 or featureNum == 24))):
                    # Below has an error with suspended games, it was fixed but if it comes back again, look here too.
                    if (seasonNo < 5 and featureNum == 3):
                        if (feature.text == ''):
                            if (cancelledGames % 2 > 0):
                                flag = True
                                cancelledGames += 1
                                break
                            elif (cancelledGames % 2 == 0):
                                flag = False
                                cancelledGames += 1
                                break
                    featureNum += 1
                    continue

                # Fixes the /'s @'s *'s etc with string parsing before pushing into list.
                if (featureNum > 0):
                    fixedText = feature.text.replace('/', '')
                    fixedText = fixedText.replace('*', '')
                    gameData.append(fixedText)
                    featureNum += 1
                    continue

                gameData.append(feature.text)
                featureNum += 1
            data.append(gameData)
        num += 1
    del data[-1]
    return data


# Function gathers a team's Roster Size, Head Coach, Game Attendance, and Game Location.
# Returns a list in suitable fashion to be converted to a pandas DF.
def gatherOtherData(table, teamName, rows, seasonNo, driver):
    data = []
    gameNum = 0
    num = 1
    gameFlag = False
    cancelledGames = 0

    locations = []
    #attendances = []

    for row in rows:
        # Checks if Head Coach text exists on webpage.
        if (checkPath(driver, '#head_coaches_div a', 'CSS')):
            headCoach = driver.find_element(By.CSS_SELECTOR, '#head_coaches_div a')
            coach = headCoach.text
        else:
            coach = 'N/A'

        if (((gameFlag == False and num % 2 > 0) or (gameFlag == True and num % 2 == 0)) and num >= 3):
            if (checkPath(driver, '/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr['+str(num)+']/td[3]', 'XPATH')):
                gameScore = table.find_element(By.XPATH, '/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr['+str(num)+']/td[3]')
            else:
                #locations.append('N/A')
                #gameNum += 1
                continue

            # Check for suspended games / games that mess with the ordering of games in the HTML.
            if (gameScore.text == '-' or gameScore.text == '' or (seasonNo >= 4 and (gameScore.text.find('W') == -1 and gameScore.text.find('L') == -1))):
                locations.append('-')
                #attendance.append(-1)
                if (cancelledGames % 2 > 0):
                    gameFlag = False
                    cancelledGames += 1
                elif (cancelledGames % 2 == 0):
                    gameFlag = True
                    cancelledGames += 1

            # Gathers location and attendance data of each game in a given season.
            else:
                # Checks to see if link even exists. -----> ERROR WITH ADAMS ST.
                if (checkPath(driver, '/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr['+str(num)+']/td[3]/a', 'XPATH')):
                    temp = table.find_element(By.XPATH, '/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr['+str(num)+']/td[3]/a')
                    temp.click()
                    driver.switch_to.window(driver.window_handles[1])

                    locationXpath = '/html/body/div[2]/table[3]/tbody/tr[2]/td[2]'
                    #attendanceXpath = '/html/body/div[2]/table[3]/tbody/tr[3]/td[2]' /html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr[21]

                    if (checkPath(driver, locationXpath, 'XPATH')):
                        gameLocation = driver.find_element(By.XPATH, locationXpath)
                        location = gameLocation.text
                    else:
                        location = '-'

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                # In the event there isn't a hyperlink attached to the score.
                else:
                    location = '-'
                    if (cancelledGames % 2 > 0):
                        gameFlag = False
                        cancelledGames += 1
                    elif (cancelledGames % 2 == 0):
                        gameFlag = True
                        cancelledGames += 1

                #if (checkPath(driver, attendanceXpath, 'XPATH')):
                #    attendancePath = driver.find_element(By.XPATH, attendanceXpath)
                #    attendance = attendancePath.text
                #else:
                #    attendance = '-'

                locations.append(location)
                #attendances.append(attendance)
                
            gameNum += 1
        num += 1

    # Gathers a team's season's roster size.
    seasonRedirect = driver.find_element(By.XPATH, '/html/body/div[2]/a[2]')
    seasonRedirect.click()
    roster = driver.find_elements(By.CSS_SELECTOR, '#stat_grid a')
    rosterSize = len(roster)
    driver.back()

    temp = []

    for i in range(0, gameNum, 1):
        temp = [teamName, coach, rosterSize, locations[i]]
        data.append(temp)
    return data   


# Function gathers a given team's season history for the last 11 seasons.
def gatherSeasonHistory(table, teamName, driver, type):
    seasonData = []
    seasonNo = 0
    num = 1
    flag = False

    # Array full of seasons desired to acquire data from.
    seasons = ['2021-22', '2020-21', '2019-20', '2018-19', '2017-18', '2016-17', '2015-16', '2014-15', '2013-14', '2012-13', '2011-12']

    # Gathers last eleven years of seasons (2022-2012)
    # Can be shortened or increased for how many seasons are desired
    headerSeasons = table.find_elements(By.CSS_SELECTOR, '.heading a')
    for i in range(0, 22):
        if (num % 2 != 0):
            # Flag for if a season link is missing, ends loop prematurely.
            if (flag and num == 21):
                break
            # Edge case for if a team has less than ten seasons, example: Lynn.
            if (i >= len(headerSeasons) * 2):
                break
            header = table.find_element(By.CSS_SELECTOR, '.heading')

            season = header.find_element(By.XPATH, 'td/div/span['+str(num)+']/a')
            # Some teams are missing season(s).
            # Below is the season cutoff you DON'T want scraped.
            # This is here if multiple seasons are skipped. Example: Moravian
            if (int(season.text.split('-')[0]) <= 2010):
                break
            elif (seasons[seasonNo] != season.text):
                flag = True
                seasonNo += 1

            season.click()
            # Sometimes a team has a "Unable to find player" error.
            if (driver.find_elements(By.CSS_SELECTOR, 'pre')):
                driver.back()
                break
            
            table = driver.find_element(By.CSS_SELECTOR, '#game_breakdown_div .mytable')
            if (type == 'general'):
                seasonData.extend(gatherSeasonData(table, teamName, seasonNo))
            elif (type == 'other'):
                rows = table.find_elements(By.CSS_SELECTOR, 'tr')
                seasonData.extend(gatherOtherData(table, teamName, rows, seasonNo, driver))
                table = driver.find_element(By.CSS_SELECTOR, '#game_breakdown_div .mytable')
            seasonNo += 1
        num += 1

    return seasonData


# Function gathers a multitude of a team's season data using team name array.
# Returns lacrosse data as 'general' datatype or 
# Returns roster data/head coach data/stadium capacity data as 'other' datatype 
# from NCAA stats website.
def findTeamSeasonData(teams, headers, division, dataType):
    driver = launchBrowser("https://stats.ncaa.org/")
    driver.maximize_window()
    featureData = []
    for team in teams:
        print(team)
        #time.sleep(2)
        search = driver.find_element(By.CSS_SELECTOR, '#org_name')
        search.send_keys(team)
        #time.sleep(2)
        dropDown = driver.find_element(By.CSS_SELECTOR, '#ui-id-1')
        teamOptions = dropDown.find_elements(By.CSS_SELECTOR, 'a')
        # Matches the team to drop down selection
        for drop in teamOptions:
            # This is a temporary fix, error occurs when a team conference has a '-' included.
            if (drop.text.find('G-MAC') != -1 or drop.text.find('Pac-12') != -1):
                teamName = drop.text.rsplit('-', 2)
            else:
                teamName = drop.text.rsplit('-', 1)
            if (teamName[0][:-1] == team):
                drop.click()
                break
        sportSelect = driver.find_element(By.CSS_SELECTOR, '#contentarea')
        sportRedirect = sportSelect.find_elements(By.CSS_SELECTOR, 'a')
        for redirect in sportRedirect:
            if (redirect.text.find("Men's Lacrosse") != -1):
                redirect.click()
                break
        #time.sleep(2)
        if (dataType == 'general'):
            seasonRedirect = driver.find_element(By.XPATH, '/html/body/div[2]/a[3]')
            seasonRedirect.click()
            # Checks if seasons are even available on client side.
            if (driver.find_elements(By.CSS_SELECTOR, 'pre')):
                driver.back()
                continue

            table = driver.find_element(By.CSS_SELECTOR, '#game_breakdown_div .mytable')
            teamSeasonData = gatherSeasonHistory(table, team, driver, 'general')

            # Creates CSV for individual teams.
            teamData = pd.DataFrame(teamSeasonData, columns=headers)
            teamData.to_csv(str(team)+"Lacrosse2012-2021.csv", index=False)
            featureData += teamSeasonData

        elif (dataType == 'other'):
            seasonRedirect = driver.find_element(By.XPATH, '/html/body/div[2]/a[3]')
            seasonRedirect.click()
            # Checks if seasons are even available on client side.
            if (driver.find_elements(By.CSS_SELECTOR, 'pre')):
                driver.back()
                continue

            table = driver.find_element(By.CSS_SELECTOR, '#game_breakdown_div .mytable')
            otherSeasonData = gatherSeasonHistory(table, team, driver, 'other')

            # Creates CSV for individual teams.
            otherData = pd.DataFrame(otherSeasonData, columns=headers)
            otherData.to_csv(str(team)+"otherLacrosseData2012-2021.csv", index=False)
            featureData += otherSeasonData

    if (dataType == 'general'):
        lacrosseData = pd.DataFrame(featureData, columns=headers)
        lacrosseData.to_csv(division+"lacrosseData.csv", index=False)
    elif (dataType == 'other'):
        otherData = pd.DataFrame(featureData, columns=headers)
        otherData.to_csv(division+"otherLacrosseData.csv", index=False)
    return


# *************************************************** #

# CALLING SECTION

# *************************************************** #

#headersPath = '/html/body/div[2]/div[3]/table/tbody/tr/td/table/tbody/tr/th'
#generalHeaders = gatherHeaders(headersPath)
#extraHeaders = ['Team', 'Head Coach', 'Roster Size', 'Location']
#laxteams = gatherTeamNames()
#errorArray = ['Utah'] 

# 0-73 D1 Teams
#d1 = laxteams[0:73]
# 73 - 148 D2 Teams
#d2 = laxteams[73:148]
# 148 - end D3 Teams
#d3 = laxteams[148:]
#findTeamSeasonData(errorArray, generalHeaders, 'lacrosseData', 'general')
#findTeamSeasonData(d2, extraHeaders, 'lacrosseData', 'other')
#findTeamSeasonData(d3, extraHeaders, 'lacrosseData', 'other')
