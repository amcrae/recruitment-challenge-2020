# -*- coding: utf-8 -*-
""" 
Download April 2020 electricity consumption and compare it
 to the average of previous years.

Created on Fri Apr 23 13:29:41 2021
@author: andrew
"""
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
print( df_averaged.info() )
print( df_averaged.head(32) )
df_averaged.to_csv('data/QLD_demand_2020_projected.csv')

# When trying to compare the different data sets it will be easier to
# convert the representations to the same time series format.
# The April actuals are nearly in the right format, just have to drop some surplus columns.
# The historical projection will need un-pivoting plus generation 
# of new time codes to match the timeslot column they came from.

