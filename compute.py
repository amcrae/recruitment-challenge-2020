# -*- coding: utf-8 -*-
""" 
Download April 2020 electricity consumption of Qld and compare it
 to the average of previous years for that state.

Most twists, turns, false leads, and red herrings are preserved in comments.

Created on Fri Apr 23 13:29:41 2021
@author: andrew
"""
import datetime
import numpy as np
import pandas as pd

from data_wrangler import download_AEMO_month

suppliedDataFiles=[
    "data/QLD_Demand_2015.csv",
    "data/QLD_demand_2016.csv",
    "data/QLD_demand_2017.csv",
    "data/QLD_demand_2018.csv",
    "data/QLD_demand_2019.csv"
]

# Req R2.
wrangled = download_AEMO_month(2020,4)
# print( wrangled )
aprilFilePath = wrangled["filepath"]
df_april = pd.read_csv(aprilFilePath, index_col="SETTLEMENTDATE")
# print( df_april.describe() )

# Req R3.
def unionHistory(historicAEMOyearlyCSVs):
    df_answer = pd.DataFrame()
    for fname in historicAEMOyearlyCSVs:
        year_df = pd.read_csv(fname, index_col=("Year","Month","Day"))
        df_answer = df_answer.append(year_df)
    return df_answer

df_history = unionHistory(suppliedDataFiles)

grouped = df_history.groupby(['Month','Day'])
df_averaged = grouped.aggregate(np.mean)
df_averaged.columns
# del df_averaged["Year"]
#print("=== df_averaged === ")
#print( df_averaged.shape )
#print( df_averaged.columns )
#print( df_averaged.index )
#print( df_averaged.info() )
#print( df_averaged.head(32) )
df_averaged.to_csv('data/QLD_demand_2020_projected.csv')

del df_history  #don't need this in memory any more.

# R4.
# When trying to compare the different data sets it will be easier to
# convert the representations to the same time series format.

# The historical projection will need un-pivoting plus generation 
# of new time codes to match the timeslot column they came from.
# Luckily there seems to be a built-in pandas function which does un-pivoting.
print("Unpivoting year projection...")

# For the longest time I could not figure out how to create a column derived 
# from multiple columns using the pure pandas syntax.
#  So it was back to (slow) Python iteration just to get the job done.
#for indexer,row in df_unpivoted.iterrows():
#    df_unpivoted.loc[indexer,'Timecode2'] = \
#    '2020-' + ("%02d" % row['Month']) + '-' + ("%02d" % row["Day"])  + ' ' \
#    +("%02d" % (row['Slot'] // 60)) + ':' + ("%02d" % (row['Slot'] % 60)) + ':00'

# But that was not needed when I figured the approach that works in Pandas
# is to build the dataframe one column at a time, so no explicit loops are needed.

#-- The stack() unpivots OK but creates a multi-level indexed Series that I can't use.
# df_averaged.set_index(['Month','Day'],inplace=True)  #Didn't really help.
ser_unpivoted = df_averaged.stack(dropna=False)
ser_unpivoted.index.set_names(['Month','Day','Slot'],inplace=True)
# Turn slot numbers into minutes of the day.
ser_unpivoted.index = ser_unpivoted.index.map(lambda x: (int(x[0]), int(x[1]), 30*int(x[2])) )
#print("=== ser_unpivoted ===")
#print( ser_unpivoted.shape )
#print( ser_unpivoted.index )
#print( ser_unpivoted.head(10) )
df_unpivoted = pd.DataFrame(ser_unpivoted,columns=["Demand"]).reset_index()
#print("=== df_unpivoted ===")
#print( df_unpivoted.head(50) )
# One column at a time is the Pandas way (?)
df_unpivoted['Year'] = int(2020)
df_unpivoted['Hour'] = df_unpivoted['Slot'] // 60
df_unpivoted['Minute'] = df_unpivoted['Slot'] % 60
df_unpivoted.insert(
    0, 
    "Timestamp",
    pd.to_datetime(df_unpivoted[['Year','Month','Day','Hour','Minute']]) 
)

#--
# Unfortunately melt complains the index columns are not present when they clearly are. 
# It was once again StackOverflow to the rescue, suggesting 
# the mysterious "trick" needed was to "reset" (!!) the index prior to melt.
"""
df_unpivoted = df_averaged.reset_index().melt(
    id_vars=["Month","Day"], 
    var_name="Slot",
    value_name="DEMAND"
)
print(df_unpivoted.info())
"""
# The result of melt was still a MultiIndex that I could not figure out how to use.

# And sorting simply does nothing. Initially I had no idea why. 
# Possibly because when I first wrote this the Slots from melt were objects 
# that had not beeen cast to either strings or ints yet, so were not sortable.
#df_unpivoted.sort_index(axis=0, level=2, kind='quicksort', inplace=True)
#df_unpivoted.sort_index(axis=0, level=1, kind='mergesort', inplace=True)
#df_unpivoted = df_unpivoted.reset_index().sort_index(axis=0,level=1,kind='mergesort')

#print( type(df_unpivoted), df_unpivoted.shape, )
#print( df_unpivoted.columns )
#print( df_unpivoted.head(50) )
#print( df_unpivoted.tail(50) )

print("=== df_projected ===")
df_projected=df_unpivoted[["Timestamp","Demand"]]
aprilStart = pd.to_datetime('2020-04-01 00:00')
mayStart = pd.to_datetime('2020-05-01 00:00')
df_april_projected=df_projected[(aprilStart<df_projected["Timestamp"]) & (df_projected["Timestamp"]<mayStart) ]
print( df_april_projected.info() )
print( df_april_projected.head(50) )

# The April actuals are nearly in the right format, just have to drop some surplus columns
#  and convert the settlementdate to a TimeSeries index.
#print( df_april.info() )
df_april_dated = pd.DataFrame(df_april,columns=["TOTALDEMAND"]).reset_index()
#print( df_april_dated.info() )
df_april_dated.insert(
    0,
    "Timestamp",
    pd.to_datetime(df_april_dated["SETTLEMENTDATE"],format='%Y/%m/%d %H:%M:%S') 
)
del df_april_dated["SETTLEMENTDATE"]
print("April shape:", df_april_dated.shape, df_april_dated.index )
print( df_april_dated.info() )
print( df_april_dated.head(10) )

