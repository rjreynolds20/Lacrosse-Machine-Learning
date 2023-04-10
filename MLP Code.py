import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score


# THE FOLLOWING BELOW WAS DONE IN JUPYTER NOTEBOOK AND MOVED TO VSCODE FOR GITHUB.

data=pd.read_csv("Clearing Cleaned.csv", thousands=",")
np.set_printoptions(suppress=True)

from sklearn.preprocessing import OneHotEncoder

ohe = OneHotEncoder()

feature_array = ohe.fit_transform(data[['Home/Neutral/Away']]).toarray()
feature_labels = ohe.categories_
feature_labels = np.array(feature_labels).ravel()
features = pd.DataFrame(feature_array, columns=feature_labels)
lax = data.drop(columns=['Team', 'Date', 'Home/Neutral/Away', 'Opponent', 'Points', 'OPoints'])
lax = pd.concat([features, lax],axis=1)

lax.rename(index=str, columns={-1:'Away', 0:'Neutral', 1:'Home'}, inplace=True)

lax['Pen Time'] = lax['Pen Time'].astype(float)
lax['OPen Time'] = lax['OPen Time'].astype(float)
lax['GameTime Difference'] = lax['GameTime Difference'].astype(float)

lax.head()

X = lax[lax.columns[:-1]].to_numpy()
y = lax[lax.columns[-1]].to_numpy()

#Training data - everything up until 2022 season.
#Testing data - 2022 season.


# For 2014-2020
X_train, X_test = X[:32256], X[32256:35994]
y_train, y_test = y[:32256], y[32256:35994]

# For 2014-2021
#X_train, X_test = X[:35994], X[35994:]
#y_train, y_test = y[:35994], y[35994:]

from sklearn.model_selection import GridSearchCV

# hyperparameter grid
hp_grid = [{'activation':['logistic', 'tanh'], 
            'hidden_layer_sizes':[[40, 100, 150], [40, 150, 100], [100, 40, 150], [100, 150, 40], [150, 40, 100], [150, 100, 40]],
            'random_state': [234, 418, 739]},
           {'learning_rate_init':[0.01, 0.001]}]

# create the model
model = MLPClassifier()

# create the grid object
grid_search = GridSearchCV(model, hp_grid, cv=5, scoring='accuracy', return_train_score=False)

grid_search.fit(X_train, y_train)

results = grid_search.cv_results_

for mean_score, params in zip(results['mean_test_score'], results['params']):
    print(mean_score, params)

the_best = grid_search.best_estimator_

print(the_best)

clf = MLPClassifier(hidden_layer_sizes={40,150,100},
                   activation='logistic', #tanh, logisitic, relu,
                   random_state=77,
                   verbose=True,
                   learning_rate_init=0.001,
                   max_iter=300,
                   )

from sklearn.model_selection import cross_val_score

clf.fit(X_train, y_train)

cross_val_score(clf, X_train, y_train, cv=5, scoring="accuracy")

from sklearn import metrics
from sklearn.metrics import accuracy_score

predictions_test = clf.predict(X_test)

test_score = accuracy_score(y_test, predictions_test)
print("score on test data: ", test_score)

# Gathers averages of a team over 2022 season.
def averageFeatures(teamName, fieldAdvantage, position, df, year):
    # 18 columns excluding home/neutral/away/team/date
    newData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    count = 0
    
    if (position == 1):
        if (fieldAdvantage == 'Home'):
            newData[2] = 1
        elif (fieldAdvantage == 'Away'):
            newData[0] = 1
        else:
            newData[1] = 1
            
        for row in range(0, len(df), 1):
            date = df[row][1].rsplit('/', 1)
            if (df[row][0] == teamName and date[1] == year):
                for feature in range(3, 21, 1):
                    newData[feature] += df[row][feature]
                count += 1
       
        if (count == 0):
            for row in range(0, len(df), 1):
                date = df[row][1].rsplit('/', 1) # uses -2 years because 2020 was cancelled.
                if (df[row][0] == teamName and int(date[1]) == int(year) - 1):
                    for feature in range(3, 21, 1):
                        newData[feature] += df[row][feature]
                    count += 1
                    
        averages = []
        for i in range(0, len(newData), 1):
            if (i == 0):
                averages.append(float(newData[0]))
                continue
            elif (i == 1):
                averages.append(float(newData[1]))
                continue
            elif (i == 2):
                averages.append(float(newData[2]))
                continue
            elif (i == 3):
                averages.append(0)
                continue
            elif (i == 6):
                continue
            averages.append(float(newData[i]) / count)
            
            
    elif (position == 2):
        newData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for row in range(0, len(df), 1):
            date = df[row][1].rsplit('/', 1)
            if (df[row][21] == teamName and date[1] == year):
                for feature in range(22, 39, 1):
                    newData[feature-22] += df[row][feature]
                count += 1

        if (count == 0):
            for row in range(0, len(df), 1):
                date = df[row][1].rsplit('/', 1)
                if (df[row][21] == teamName and int(date[1]) == int(year) - 1):
                    for feature in range(22, 39, 1):
                        newData[feature-22] += df[row][feature]
                    count += 1
                    
        averages = []
        for i in range(0, len(newData), 1):
            if (i == 2):
                continue
            averages.append(float(newData[i]) / count)
            
    return averages


# Gathers averages of games between team A and team B.
def averageAB(A, B, AfieldAdvantage, df, year):
    # Away, Neutral, Home, OT
    abAverage = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    count = 0
    num = 4
    
    if (AfieldAdvantage == 'Home'):
        abAverage[2] = 1
    elif (AfieldAdvantage == 'Away'):
        abAverage[0] = 1
    else:
        abAverage[1] = 1
    
    for row in range(0, len(df), 1):
        date = df[row][1].rsplit('/', 1)
        if ((df[row][0] == A and df[row][21] == B) and (date[1] == year)):
            for feature in range(4, len(df[row]) - 1, 1):
                if (feature == 5 or feature == 21 or feature == 23):
                    continue   
                abAverage[num] += df[row][feature]
                num += 1
            num = 4
            count += 1
            
    if (count == 0):
        #print('No Previous Games')
        return abAverage
    
    # For when # games > 1.
    averages = []
    for i in range(0, len(abAverage), 1):
        if (i == 0):
            averages.append(float(abAverage[0]))
            continue
        elif (i == 1):
            averages.append(float(abAverage[1]))
            continue
        elif (i == 2):
            averages.append(float(abAverage[2]))
            continue
        elif (i == 3):
            averages.append(0)
            continue
        averages.append(float(abAverage[i]) / count)
    
    return averages


# Makes a prediction on a lacrosse game.
# Takes, team A, team B, field advantages of teams, dataframe, and which type of prediction type.
# 1 = weighed prediction type, more accurate. 2 = prediction based purely on averages of teams.
def predictGame(A, B, AfieldAdvantage, BfieldAdvantage, df, year):
    # Call function to average all features of all A's games.
        # Input should include A, df, years of how far back.
    homeTeam = averageFeatures(A, AfieldAdvantage, 1, df, year)
        
    # Call function to average all features of all B's games.
        # Input should include A, df, years of how far back.
    awayTeam = averageFeatures(B, BfieldAdvantage, 2, df, year)
    
    # Combine average (A and B) dataframes into a single row usable for prediction on model.
    row = homeTeam + awayTeam
    
    # Combine AB averages, weigh 60% on AB games, 40% on team averages.
    newRow = [row[0], row[1], row[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, row[19],
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, row[35], 0]

    previousGamesAverage = averageAB(A, B, AfieldAdvantage, df, year)

    for i in range (4, len(newRow), 1):
        if (i == 19 or i == 35):
            continue
        newRow[i] = ((row[i] * 0.4) + (previousGamesAverage[i] * 0.6)) / 2
    
    #print(A + " " + B)
    # Left = Loss, Right = Win
    #print(clf.predict_proba(np.array([newRow,]).reshape(1,-1)))

    prediction = clf.predict(np.array([newRow,]).reshape(1,-1))
    #print(prediction)

    #if (prediction == 1):
    #    print(A)
    #else:
    #    print(B)
    return prediction


# Tests the model on a given year.
# Year should be one year before year you are predicting
def testModel(data, year):
    df = data.values
    results = []

    # Takes ~6 minutes
    for i in range(35994, len(df), 1):
        if (data.values[i][3] == 1):
            results.append(predictGame(df[i][0], df[i][21], 'Home', 'Away', df, year))
        elif (data.values[i][3] == -1):
            results.append(predictGame(df[i][0], df[i][21], 'Away', 'Home', df, year))
        else:
            results.append(predictGame(df[i][0], df[i][21], 'Neutral', 'Neutral', df, year))

    # 2022 Season Games Results:
    seasonOutcomes = y[35994:]

    test_score = accuracy_score(seasonOutcomes, results)
    print("score on test data: ", test_score)
    return

#predictGame('', '', 'Home', 'Away', data.values, '')
testModel(data, '2021')
# 0.7097156398104265 accuracy on 2022 games using 2021 statistics.