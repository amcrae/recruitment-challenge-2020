# -*- coding: utf-8 -*-
""" 
Download April 2020 electricity consumption of Qld and compare it
 to the average of previous years for that state.

Implements most of requirement R5 except the 29 April figure is not regenerated.

Dependencies:
Package         Minimum     Also Tested
-------------   --------    ------------
numpy           1.18.5      1.20.0
pandas          0.24.2      1.2.0
requests        2.9.1       2.25.1
-------------   --------    ------------

Created on Fri Apr 23 13:29:41 2021
@author: andrew
"""
from typing import List

import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_wrangler import get_AEMO_demand_month, get_AEMO_demand_year

ListInt=List[int]

# Req R2.
df_april = get_AEMO_demand_month(2020,4)

# Req R3.
def unionYearHistory(demand_years_ad:ListInt) -> pd.DataFrame:
    """ Return multiple years of AEMO electricity demand data. """
    df_answer = pd.DataFrame()
    for y_ad in demand_years_ad:
        year_df = get_AEMO_demand_year(y_ad)
        df_answer = df_answer.append(year_df)
    return df_answer

df_history = unionYearHistory( [y_ad for y_ad in range(2015,2020)] )

# Average all years to implement Req R3.
grouped = df_history.groupby(['Month','Day','Hour','Minute'])
df_averaged = grouped.aggregate(np.mean)
del df_averaged["Year"]
df_averaged.reset_index(inplace=True)
print("=== df_averaged === ")
print( df_averaged.shape )
print( df_averaged.columns )
print( df_averaged.head(50), "etc..." )

del df_history  # We don't need this in memory any more.

# Throw away any unneeded columns and set Year of the projection to be 2020.
df_projected=df_averaged[['Month','Day','Hour','Minute','Demand']]
df_projected['Year'] = 2020
# Need to recalculate the timestamps since they were destroyed in the statistical abstraction.
df_projected.insert(
    0, 
    "Timestamp",
    pd.to_datetime(df_projected[['Year','Month','Day','Hour','Minute']]) 
)
df_projected.set_index(['Year','Month','Day','Hour','Minute'],inplace=True)
# Save it to meet requirement R3.
df_projected.to_csv('data/QLD_demand_2020_projected.csv')

# Filtering the projected average down to April only, for the comparison and diagramming.
aprilStart = pd.to_datetime('2020-04-01 00:00')
mayStart = pd.to_datetime('2020-05-01 00:00')
df_april_projected=df_projected[(aprilStart<df_projected["Timestamp"]) & (df_projected["Timestamp"]<mayStart) ]
df_april_projected.set_index(['Timestamp'],inplace=True)
df_april_projected = df_april_projected.rename(columns={'Demand':'PROJECTED'})

# The April actuals are nearly in the right format, just have to drop some surplus columns
df_april_actual = pd.DataFrame(df_april,columns=["Timestamp","TOTALDEMAND"])
df_april_actual.set_index(["Timestamp"], inplace=True)
df_april_actual = df_april_actual.rename(columns={'TOTALDEMAND':'APRIL2020'})

# Cannot easily compare until they are in the same DataFrame, so do a fast join on the indexed timestamps.
df_combined=pd.merge(df_april_projected, df_april_actual, how='inner', left_index=True, right_index=True)
print( df_combined.head(30), "etc..." )

df_comparison = pd.DataFrame(df_combined,copy=True).reset_index()
df_comparison["DIFFERENCE"] = df_comparison["APRIL2020"] - df_comparison["PROJECTED"]
del df_comparison["APRIL2020"]
del df_comparison["PROJECTED"]
print( df_comparison.head(30), "etc..." )

# Bonus, investigate hypothesis that main cause of difference is 
# an activity that reoccurs at particular times of day.
df_hour_corr=df_comparison.reset_index()
df_hour_corr["Hour"]=df_hour_corr["Timestamp"].map( lambda x: x.hour )
df_hour_corr["ABSDIFF"]=abs(df_hour_corr["DIFFERENCE"])
del df_hour_corr["Timestamp"]
del df_hour_corr["index"]
del df_hour_corr["DIFFERENCE"]
hgroup = df_hour_corr.groupby(['Hour'])
df_hour_corr= hgroup.aggregate(np.mean).nlargest(3,'ABSDIFF')
df_hour_corr.rename(columns={'ABSDIFF':'AvgABSDIFF'},inplace=True)
print("The hours of the day with the highest average absolute difference were:\n", df_hour_corr)
top_hours=df_hour_corr.index
hour_hypotheses={4:"Heating", 7:"Breakfast", 12:"Lunch", 15:"Cooling", 18:"Dinner"}
for h,r in hour_hypotheses.items():
    print( r, "_IS_" if (h in top_hours) else "is not", "a strong suspect for cause of difference." )

# Answer the main question, how much more or less was April?
month_difference_MWh = sum(df_comparison["DIFFERENCE"]*0.5) # Was 30minute intervals of MW.
print("~~~~~~~~~~~~~~~~~~~~~~~ 👀 👓 😲 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print( "ANSWER: April 2020 was %+d MWh more than projected historical average." % month_difference_MWh)

# For possible use in javascript visualisations.
df_combined.to_json('data/QLD_demand_202004_compared.json',orient='columns')

# Finally, the graph. R4.
df_combined.reset_index(inplace=True)  #Indexed columns cease being available as data columns.
plt.close('all')
plot1 = df_combined.plot.line(
    x="Timestamp",
    title="Comparison of April2020 electricity consumption versus historical average",
    figsize=(60,12)
)
f1=plt.figure(1)
f1.savefig("figures/2020 April Comparison.png")     # R5.

# Graphing the difference has less intutive meaning than just showing both lines, IMO.
df_comparison.plot.line(
    x="Timestamp",
    title="Comparison of April2020 electricity consumption versus historical average",
    figsize=(60,12)
)
f2 = plt.figure(2)
f2.savefig("figures/2020 April Difference.png")     # R5.
plt.show()
print("Interactive figures have been displayed.")
