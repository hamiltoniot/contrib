#!/bin/python

# this is required to access your data
API_KEY="XXXXX_ENTER_HERE_XXXXXX"

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

# Lets use data from 10 minutes ago
nw = datetime.datetime.utcnow()
nw = nw - datetime.timedelta(minutes=9)
now_ts = nw.isoformat()+"Z"
thn = nw - datetime.timedelta(minutes=10)
then_ts = thn.isoformat()+"Z"

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
        return get_with_pagination(device, body["nextFrom"], time_end, rollup, body, skipfirst=True)
    else:
        return body

# this is a wrapper around get_with_pagination that returns the results as a pandas dataframe
def get_pandas_dataframes(device, time_start, time_end, rollup="1m", auth=None):
    data = get_with_pagination(device, time_start, time_end, rollup, auth=auth)
    rz = data["results"]
    dataframes = {}
    for sensor in rz:
        rows = []
        sns = rz[sensor]
        for i in range(len(sns["counts"])):
            rows.append({
                "min":sns["minimums"][i],
                "mean":sns["means"][i],
                "max":sns["maximums"][i],
                "count":sns["counts"][i],
            })
        df = pd.DataFrame(data=rows)
        df = df.set_index(pd.DatetimeIndex(sns["times"]))
        dataframes[sensor] = df
    return dataframes

site="default" #this is where devices get placed by default
rv = list_devices(site,auth=API_KEY)
print "Here are the registered devices in site=%s" % site
print json.dumps(rv,indent=1)
# pick the first device and try get data from it
deviceid=rv["results"].keys()[0]
print "Getting the last 10 minutes of data from device %s" % deviceid
print "From: %s" % then_ts
print "To: %s" % now_ts
rv = get_with_pagination(deviceid, then_ts, now_ts, rollup="1s", auth=API_KEY)
print json.dumps(rv, indent=1)
