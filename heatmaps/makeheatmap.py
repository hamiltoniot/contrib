#!/bin/python

# this is just for example, you can use a metadata query to look this up rather
devices = {
 # devid    X   Y
 "01072D": [300, 600],
 "010730": [900,  1000],
 "010734": [400,  1800],
 "010736": [900,  2500],
 "010732": [300,  3200],
 "010733": [2560, 1000],
 "01072A": [2700, 1500],
 "01072C": [2850, 1800],
}
# this is required to access your data
API_KEY="XXXXX_ENTER_HERE_XXXXXX"

# required imports for this demo
import pandas as pd
import requests
import numpy as np
import datetime
import requests
import scipy.interpolate
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
import math
import datetime
import sys
import os


# Lets use data from 10 minutes ago
nw = datetime.datetime.utcnow()
nw = nw - datetime.timedelta(minutes=9)
now_ts = nw.isoformat()+"Z"
thn = nw - datetime.timedelta(minutes=1)
then_ts = thn.isoformat()+"Z"


# This is a reusable utility method that gets a range of data for a hamilton sensor. We don't really need
# it for this demo because we are only querying one data point, but if you are doing a timeseries plot
# it is quite handy.
# the time_start and time_end strings are RFC3339 format or unix nanoseconds-since-the-epoch nubmers
def get_with_pagination(device, time_start, time_end, rollup="1m", into=None, skipfirst=False, auth=None):
    for i in range (10):
        print ("doing request")
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

# get the data for our devices
data = []
for did in devices:
    device_data = get_pandas_dataframes(did, then_ts, now_ts, rollup="1m", auth=API_KEY)
    data.append([devices[did][0], devices[did][1], device_data["air_temp"].iloc[0]["mean"]])
data = np.array(data)

# create the plot. This is a little specific to our deployment
mpl.rc("savefig", dpi=200)
xmin = 100
xmax = 3000
ymin = 200
ymax = 3600
def main(data, vmin=None, vmax=None, extra=None, filename=None):
    x = data[...,0]
    y = data[...,1]
    a = data[...,2]
    xi, yi = np.mgrid[xmin:xmax:500j, ymin:ymax:500j]
    a_rescale = rescaled_interp(x, y, a, xi, yi)
    plot(x, y, a, a_rescale, 'Rescaled', vmin, vmax, extra, filename)
    plt.show()


def rescaled_interp(x, y, a, xi, yi):
    a_rescaled = (a - a.min()) / a.ptp()
    rbf = scipy.interpolate.Rbf(x, y, a_rescaled)
    ai = rbf(xi, yi)
    ai = a.ptp() * ai + a.min()
    return ai

def plot(x, y, a, ai, title, vmin=None, vmax=None, extra=None, filename=None):
    fig, ax = plt.subplots()
    img=mpimg.imread('mcrop.png')
    fig.set_size_inches(16,16)
    fig.set_dpi(200)
    if vmin==None:
        vmin = a.min()-1.5
        vmax = a.max()+1.5
    im = ax.imshow(ai.T, origin='lower',
                   extent=[xmin,xmax,ymin,ymax],vmin=vmin, vmax=vmax)
    im2 = plt.imshow(img)
    ax.scatter(x, y, c="white", vmin=vmin, vmax=vmax)
    for i in range(len(a)):
        ax.annotate(" %.2f" % (a[i]), (x[i]+4,y[i]+8), size="x-small",color="white", weight="bold", backgroundcolor=(0,0,0,0.3))
    ax.annotate(then_ts, (20, 80), size="x-large")
    if extra != None:
        ax.annotate(extra, (20, 10), size="x-large")
    ax.axis("off")
    fig.colorbar(im)
    fig.savefig("outfile.png", bbox_inches="tight")

# you can adjust the temperature range here
main(data,15,21, "AIR TEMPERATURE", "temp")
