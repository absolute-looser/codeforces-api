# coding: utf-8

# # Contest Parser v1
# Goal is to return the following table
#  
# handle | rating | contestID | problemID | success 
# --- | --- | --- | --- | --- | ---
# handle0 | 1234 | 633 | A | 1
# handle0 | 1234 | 633 | B | 1
# handle0 | 1234 | 633 | C | 0
# 

import requests
import pandas as pd

def getSolveSuccessDF(contestID):
#contestID = 671
    urlbase = 'http://codeforces.com/api/'
    method = 'contest.standings'
    maxcnt = 100000
    #http://codeforces.com/api/contest.standings?contestId=566&from=1&count=5&showUnofficial=true
    url = urlbase + method + '?contestId=' + str(contestID) + '&from=1&count=' + str(maxcnt) + '&showUnofficial=false'
    r = requests.get(url).json()['result']
    rows = r['rows']
    problems = r['problems']
    contest = r['contest']

    # CHECK TO MAKE SURE THAT TEAMS ARE NOT ALLOWED!!!
    for r in rows: # for each person
	if len(r['party']['members']) > 1:
	    raise "This contest allows teams. ELO scores are not well-defined."

    users = []
    points = []
    for r in rows:
	users.append(r['party']['members'][0]['handle'])
	
	userpts = [0]*len(problems)
	for i in range(len(problems)):
	    userpts[i] = r['problemResults'][i]['points']
	points.append([1 if u > 0 else 0 for u in userpts])


    # Grab rating changes
    method = 'contest.ratingChanges'
    url = urlbase + method + '?contestId=' + str(contestID)
    ratingchanges = requests.get(url).json()['result']
    ratingdict = dict()
    for r in ratingchanges:
	ratingdict[r['handle']] = r['oldRating']


    # Create output df 
    # start constructing dataframe
    array_out = []
    for i in range(len(users)): # for each user in the contest
	hdl = users[i]
	rating = ratingdict[hdl]
	for j, p in enumerate(problems): # for each problem in the contest, make a new row
	    temp = dict.fromkeys(['handle', 'rating', 'contestID', 'problemID', 'success'])
	    temp['handle'] = hdl
	    temp['contestID'] = contestID
	    temp['problemID'] = p['index']
	    temp['success'] = points[i][j]
	    temp['rating'] = rating
	    array_out.append(temp)

    output = pd.DataFrame.from_dict(array_out)
    return output

