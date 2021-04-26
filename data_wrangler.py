# -*- coding: utf-8 -*-
"""
This data wrangler is for Queensland electricty demand data.
The purpose of the wrangler is to provide data in an easy-to-use consistent form
regardless of the differerent formats that the original data sources provided.

In this case it gives recent month data and whole-of-year data in compatible formats,
removing the discrepancy between pivoted and unpivoted source data files.
This also identifies time blocks by their start, not by their end, so the numbers
appear at timestamps 30mins earlier than when the period demand was originally "settled".

Downloaded data is returned as Pandas DataFrames, but it is
 also cached in files in a manner relatively opaque to the caller.

Created on Fri Apr 23 08:23:35 2021
@author: andrew
"""
import sys
import os
import time
import requests
import pandas as pd

supplied_AEMO_year_data_files={
    2015: "data/QLD_Demand_2015.csv",
    2016: "data/QLD_demand_2016.csv",
    2017: "data/QLD_demand_2017.csv",
    2018: "data/QLD_demand_2018.csv",
    2019: "data/QLD_demand_2019.csv"
}

REQUEST_LOCKOUT_SECONDS=300  # Retrieval no more than once every five minutes


def get_AEMO_demand_month(Y:int, M:int, use_cached:bool=True) -> pd.DataFrame :
    """ Return recent AEMO demand data from an internally hardcoded web source.
    Keyword arguments:
        use_cached --  When True, try to use a cached file instead of doing a download.
                    Note that the cached file will still be used if it
                    has been downloaded recently (REQUEST_LOCKOUT_SECONDS) 
                    for the purpose of not hitting the AEMO service too often.
    """
    # When the parameters are (2020,4) this fulfills requirement R2.
    
    ys = str(Y)
    ms = "%02d" % (M,)
    monthcode = ys+ms
    
    folder= "data"
    filename='QLD_demand_'+monthcode+'.csv'
    downloadedRecentFile=folder+os.sep+filename
    
    try:
        fstat = os.stat(downloadedRecentFile)
        age_s = int(time.time()) - fstat.st_mtime
        print("Cached file age is %d s." % age_s, file=sys.stderr )
        if not use_cached and age_s < REQUEST_LOCKOUT_SECONDS:
            use_cached = True  # too soon.
    except FileNotFoundError:
        use_cached = False
    
    # Have determined whether file should be downloaded again.
    if use_cached:
        print("...will use cached version.", file=sys.stderr)
    else:
        AUTH_COOKIE_URL = 'https://aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data'
        RECENT_DATA_URL = 'https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_'+monthcode+'_QLD1.csv'
        
        browser_headers= [
                    {
                        "name": "Accept",
                        "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
                    },
                    {
                        "name": "Accept-Encoding",
                        "value": "gzip, deflate, br"
                    },
                    {
                        "name": "Accept-Language",
                        "value": "en-US,en;q=0.5"
                    },
                    {
                        "name": "Connection",
                        "value": "keep-alive"
                    },
                    {
                        "name": "DNT",
                        "value": "1"
                    },
                    {
                        "name": "Host",
                        "value": "aemo.com.au"
                    },
                    {
                        "name": "Referer",
                        "value": "https://aemo.com.au/aemo/apps/visualisation/index.html"
                    },
                    {
                        "name": "Upgrade-Insecure-Requests",
                        "value": "1"
                    },
                    {
                        "name": "User-Agent",
                        "value": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
                    }
        ]
        new_headers={ m["name"]:m["value"] for m in browser_headers }
        
        cookiedResponse = requests.get(AUTH_COOKIE_URL, headers=new_headers)
        cookieJar = cookiedResponse.cookies
        # print( repr(cookieJar) )
        cookieJar.set("privacy-notification","1")
        
        try: 
            res = requests.get(RECENT_DATA_URL, headers=new_headers, cookies=cookieJar)
            if 200 <= res.status_code <= 320:
                print("Server status is OK", file=sys.stderr)
            else:
                raise IOError("Cannot download recent month data, HTTP status "+str(res.status_code) )
            with open(downloadedRecentFile, 'wb') as fd:
                for chunk in res.iter_content(chunk_size=4096):
                    fd.write(chunk)
            print("downloaded finished without error.", file=sys.stderr)
        except:
            raise IOError("Cannot download recent month data")
    
    # Data definitely downloaded at this point.
    df = pd.read_csv(downloadedRecentFile)
    if not ("TOTALDEMAND" in df.columns):
        raise IOError("Unexpected data format in download.")
    print("File format test OK.", file=sys.stderr)
    
    #Add in Timestamp data type column for convenience and compatibility with the Year sets.
    df.reset_index()
    df.insert(
        0,
        "Timestamp",
        pd.to_datetime(df["SETTLEMENTDATE"],format='%Y/%m/%d %H:%M:%S') 
    )
    # To keep the month sets consistent with the Years, the 0-based slots of the Years
    # have to be emulated in the monthly data by moving the timestamps backwards 30mins.
    df["Timestamp"] = df["Timestamp"] + + pd.Timedelta(minutes=-30)
    
    return df


def get_AEMO_demand_year(year_ad:int) -> pd.DataFrame:
    """Return a year of electricity demand in a convenient format similar to
        what is returned by the recent month data function.
        The columns will still have Year,Month,Day, but also a Minute column,
        and are indexed by a new Timestamp column.
    """
    cached_file_path = supplied_AEMO_year_data_files[year_ad]
    df_history = pd.read_csv(cached_file_path, index_col=("Year","Month","Day"))
    
    # R4.
    # When trying to compare the different data sets it will be easier to
    # convert the representations to the same time series format.
    
    # The historical projection will need un-pivoting plus generation 
    # of new time codes to match the timeslot column they came from.
    # Luckily there seems to be a built-in pandas function which does un-pivoting.
    print("Unpivoting year projection...",file=sys.stderr)
    
    #-- The stack() unpivots OK but creates a multi-level indexed Series.
    ser_unpivoted = df_history.stack(dropna=False)
    ser_unpivoted.index.set_names(['Year','Month','Day','Slot'],inplace=True)
    # Turn slot numbers into minutes of the day.
    ser_unpivoted.index = ser_unpivoted.index.map( lambda x: 
        (int(x[0]), 
         int(x[1]), 
         int(x[2]), 
         # BUGFIX: Make slots 0-based to prevent date rollover to nonexistent date (eg 31 April)
         30*(int(x[3])-1))   
    )
    
    df_unpivoted = pd.DataFrame(ser_unpivoted,columns=["Demand"]).reset_index()
    
    # One column at a time is the Pandas way (?)
    df_unpivoted['Hour'] = df_unpivoted['Slot'] // 60
    df_unpivoted['Minute'] = df_unpivoted['Slot'] % 60
    df_unpivoted.insert(
        0, 
        "Timestamp",
        pd.to_datetime(df_unpivoted[['Year','Month','Day','Hour','Minute']]) 
    )

    #Don't need this, it has been converted to the hour,minute,and timestamp
    del df_unpivoted["Slot"]
    
    return df_unpivoted


if __name__ == "__main__":
    tr = get_AEMO_demand_month(2020,4)
    print( tr.info() )
    print( tr.index )
    print( tr.head(5) )
