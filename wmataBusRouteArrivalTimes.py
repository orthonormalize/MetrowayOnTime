# -*- coding: utf-8 -*-
"""
Created on Sat Jun 04 13:25:33 2016

@author: rek
"""
import urllib, json, time
import pandas as pd


# PARAMETERS:
# limit 10 calls per second
p = {
    'callsPerSecond': 2,
    'RouteID': 'MW1'}

params_NextBus = urllib.urlencode({
    # Request parameters
    'api_key': 'api key'
})

params_Schedule = urllib.urlencode({
    # Request parameters
    'RouteID': 'MW1',
    'Date': '2016-06-04',
    'IncludingVariations': 'false',
    'api_key': 'api key'
})


def cols_nextBusDF():
    return ['StopID','Direction','time','TripID','Minutes']


# MAIN:

urlSched = 'http://api.wmata.com/Bus.svc/json/jRouteSchedule?%s' % params_Schedule
sched = json.load(urllib.urlopen(urlSched))
L_DS = []
for direc in [0,1]:
    whichTrip = 0
    stops = sched['Direction'+str(direc)][whichTrip]['StopTimes']
    for ss in range(len(stops)):
        L_DS += [(direc,stops[ss]['StopID'])]

ii=-1
urlNextBus_base = 'http://api.wmata.com/NextBusService.svc/json/jPredictions?%s' % params_NextBus
nextBusDF = pd.DataFrame(index=range(0),columns=cols_nextBusDF())
while True:
    ii=ii+1
    print(ii)
    (D,S) = L_DS[(ii) % len(L_DS)]
    url = urlNextBus_base + '&StopID=' + S
    NB_result = json.load(urllib.urlopen(url))
    t = time.time()
    if ('Predictions' in NB_result):
        preds = NB_result['Predictions']
        for pred in preds:
            if ((pred['RouteID']==p['RouteID']) and (pred['DirectionNum'] == str(D))):
                nextBusDF.loc[len(nextBusDF)] = [S,str(D),str(int(t)),pred['TripID'],str(int(pred['Minutes']))]
    # Dump to CSV periodically:
    if (not((1+ii) % (1*len(L_DS)))):            
        try:
            nextBusDF.to_csv('MW1_004.csv')
        except:
            pass            
    nowTime = time.time()
    napTime = (1.0/p['callsPerSecond']) - (nowTime-t)
    time.sleep(max([0.1,napTime]))         # don't overload WMATA API  