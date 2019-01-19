#!/bin/python

# this is required to access your data
API_KEY="XXXXX_ENTER_HERE_XXXXXX"

# these are the dates you wish to export between
START_DATE="2018-06-18T00:00:00.000000Z"
END_DATE="2018-06-23T00:00:00.000000Z"
# this is the site to export from
SITE="default"

# required imports for this demo
import pandas as pd
import requests
import numpy as np
import datetime
import requests
import time
import math
import datetime
import sys
import os
import json

def list_devices(site, auth=None):
    for i in range (10):
        r = requests.post("https://api.hamiltoniot.com/v1/devices/lookup",
            json={"site":site,"constraintTags":{"_type":"sensor"}}, headers={"Authorization":auth})
        body = r.json()
        if r.status_code == 420:
            time.Sleep(0.5)
            continue
        if r.status_code == 200:
            break
        raise Exception(r.text)
    return body

# This is a reusable utility method that gets a range of data for a hamilton sensor.
# the time_start and time_end strings are RFC3339 format or unix nanoseconds-since-the-epoch nubmers
def get_with_pagination(device, time_start, time_end, rollup="1m", into=None, skipfirst=False, auth=None):
    print ("device is %s"% device)
    for i in range (10):
        r = requests.get("https://api.hamiltoniot.com/v1/data/rollup/%s?from=%s&to=%s&millis=0&rollup=%s&limit=1000" % (
        device, time_start, time_end, rollup), headers={"Authorization":auth})
        body = r.json()
        if r.status_code == 420:
            time.Sleep(0.5)
            continue
        if r.status_code == 200:
            break
        raise Exception(r.text)
    if into is not None:
        for sensor in body["results"]:
            for cat in ["times","maximums","means","minimums","counts"]:
                sidx = 1 if skipfirst else 0
                into["results"][sensor][cat].extend(body["results"][sensor][cat][sidx:])
        body["results"] = into["results"]
    if body["more"]:
        return get_with_pagination(device, body["nextFrom"], time_end, rollup, body, skipfirst=True, auth=auth)
    else:
        return body

all_devices = list_devices(SITE,auth=API_KEY)["results"].keys()
for device in all_devices:
    print ("fetching data for",device)
    ofile = open("export_%s_%s_%s.csv" % (device, START_DATE, END_DATE),'w')
    ofile.write("timestamp,date,temperature [C], relative humidity [%], illuminance [Lux]\n")
    data = get_with_pagination(device, START_DATE, END_DATE, rollup="1s", auth=API_KEY)
    if data["results"] == {}:
        print ("skipping: no data")
        continue
    times = data["results"]["air_temp"]["times"]
    dates = [datetime.datetime.fromtimestamp(x/1e9).strftime('%Y-%m-%d %H:%M:%S') for x in times]
    airtemp = data["results"]["air_temp"]["means"]
    humidity = data["results"]["air_rh"]["means"]
    illuminance = data["results"]["lux"]["means"]
    rows = zip(times,dates,airtemp,humidity,illuminance)
    for r in rows:
        ofile.write(",".join(str(x) for x in r))
        ofile.write("\n")
    ofile.write("\n")
    ofile.close()
