# -*- coding: utf-8 -*-
"""
Data wrangler for Queensland electricty demand data.
The output is in files, but the location of the file is returned.

Created on Fri Apr 23 08:23:35 2021
@author: andrew
"""
import os
import time
import requests
import pandas as pd

def download_AEMO_month(Y, M, use_cached=True):
    ys = str(Y)
    ms = "%02d" % (M,)
    monthcode = ys+ms
    
    folder= "data"
    filename='QLD_demand_'+monthcode+'.csv'
    downloadedRecentFile=folder+os.sep+filename
    
    if use_cached:
        try:
            fstat = os.stat(downloadedRecentFile)
            age_s = int(time.time()) - fstat.st_mtime
            print("Cached file age is %d s." % age_s, )
            if age_s > 60:     # does not download more than once per minute.
                use_cached = False
        except FileNotFoundError:
            use_cached = False
    
    # Have determined whether file should be downloaded again.
    if use_cached:
        print("...will use cached version.")
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
                print("Server status is OK")
            else:
                raise IOError("Cannot download recent month data, HTTP status "+str(res.status_code) )
            with open(downloadedRecentFile, 'wb') as fd:
                for chunk in res.iter_content(chunk_size=4096):
                    fd.write(chunk)
            print("downloaded finished without error.")
            df = pd.read_csv(downloadedRecentFile, index_col="SETTLEMENTDATE")
            if not ("TOTALDEMAND" in df.columns):
                raise IOError("Unexpected data format in download.")
            print("File format test OK.")
        except:
            raise IOError("Cannot download recent month data")
    
    #Data is in file (cached or refreshed)
    return {"Sucess":True, "filepath":downloadedRecentFile}


if __name__ == "__main__":
    download_AEMO_month(2020,4)
