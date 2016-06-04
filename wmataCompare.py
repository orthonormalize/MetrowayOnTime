# -*- coding: utf-8 -*-
"""
Created on Sat Jun 04 16:18:04 2016

@author: rek
"""
import urllib,json
import pandas as pd
import time
import datetime

def cols_delayMatrix():
    return ['TripID','Direction','StopID','ExpectedTime','ActualTime','DelaySeconds']

def expectedTime(tripID,stopID,sched):
    sched_tripIDs = {0:[],1:[]}
    sched_tripIDs[0] = [int(trip['TripID']) for trip in sched['Direction0']]
    sched_tripIDs[1] = [int(trip['TripID']) for trip in sched['Direction1']]
    direc = [0 if (tripID in sched_tripIDs[0]) else 1][0]
    tripDex = sched_tripIDs[direc].index(tripID)
    itinerary = sched['Direction'+str(direc)][tripDex]['StopTimes']
    stopIDs = [int(stop['StopID']) for stop in itinerary]
    stopDex = stopIDs.index(stopID)
    ET_String = itinerary[stopDex]['Time'].replace('T',' ')
    ET_unix = time.mktime(datetime.datetime.strptime(ET_String,"%Y-%m-%d %H:%M:%S").timetuple())
    return ET_unix


# MAIN:

params_Schedule = urllib.urlencode({
    # Request parameters
    'RouteID': 'MW1',
    'Date': '2016-06-04',
    'IncludingVariations': 'false',
    'api_key': 'api key'
})
urlSched = 'http://api.wmata.com/Bus.svc/json/jRouteSchedule?%s' % params_Schedule
sched = json.load(urllib.urlopen(urlSched))
#sched_tripIDs_0 = [int(trip['TripID']) for trip in sched['Direction0']]
#sched_tripIDs_1 = [int(trip['TripID']) for trip in sched['Direction1']]



DF = pd.read_csv('MW1_004.csv')
uStopID = DF.StopID.unique()
uDirection = DF.Direction.unique()
uTripID = DF.TripID.unique()

delayMatrix = pd.DataFrame(index=range(0),columns=cols_delayMatrix())
for stopID in uStopID:
    for tripID in uTripID:
        for direc in uDirection:
            df = DF[(DF.StopID==stopID) & (DF.TripID==tripID) & (DF.Direction == direc)]
            if (len(df)):
                df = df.sort_values(by='time')
                lastEntry = df.iloc[len(df)-1]
                ET = expectedTime(tripID,stopID,sched)
                LE_delaySeconds = (lastEntry.time-ET)
                delayMatrix.loc[len(delayMatrix)] = [str(tripID),str(direc),str(stopID),\
                                                    str(int(ET)),str(int(lastEntry.time)),str(int(LE_delaySeconds))]
                
                
