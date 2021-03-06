# --------------------------------------------------------------------------------------------------
#
# This script file is a simple play around with the Hamilton API from a Python perspective. This 
# file primarily deals with building am API GET request to fetch sensor data and use it.
#
# Tested On: Python 2.7.X (Ubuntu 16.04, Windows 10 (Version 1709, Build 16299.192))
# Libraries: os, requests   (These should come pre-installed with Python)
#
# Created by: Alan Herbert (hamilton@eskerfall.com)
#
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# This is the generated curl from Swagger UI that was used to build up the python under
# --------------------------------------------------------------------------------------------------

curl_test = 0       # set to anything but 1 to pass the curl request down to the host's terminal

api_type = "devapi" # either devapi or api depending on portal used

# note that you will have to replace DEVICE_ID and API_KEY with your device ID and API key in order
# for this to even remotely work. you would most likely need to change at least the dates in which
# data was requested between (the "from" and "to" flags).
curl_req = "curl -X GET \"https://" + api_type + ".hamiltoniot.com/v1/data/rollup/DEVICE_ID?" + \
           "from=2017-12-19T00%3A00%3A00%2B02%3A00&to=2018-01-19T00%3A00%3A00%2B02%" + \
           "3A00&millis=true&rollup=1d&limit=1000\" -H  \"accept: application/json\" -H " + \
           "\"Authorization: API_KEY\""

if(curl_test):      # simply runs the command in a simulated terminal, and prints results to screen
    import os
    os.system(curl_req)
    exit(0)



# --------------------------------------------------------------------------------------------------
# Actual useful non-autogenerated curl code starts here
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Imports

import requests 



# --------------------------------------------------------------------------------------------------
# Request data used

d_sensor = ""                           # for example: "01072D"

d_from   = ""                           # start time of data to be fetched.
d_to     = ""                           # end time of data to be fetched (this also works in unix
                                        # seconds, but this code sticks to RFC 3339).
                                        # for example with time zone: "2018-01-15T01:00:00-02:00"
                                        
d_millis = "true"                       # returns times in milliseconds, setting to false returns
                                        # time in nanoseconds (javascript sometimes battles with 
                                        # this accuracy).
                                        # this has been set to "true" as a default value.
                                        
d_rollup = "5m"                         # sensor data placed into 5 minute buckets.
                                        # this has been set to "5m" as a default value.

d_limit  = "1000"                       # limit number of data points to respond with in a request.
                                        # this has been set to "1000" as a default value.

d_header = "application/json"           # required header information.
d_auth   = ""                           # auth key required in header too.
                                        # this can be obtained from the "API Access" tab on the 
                                        # Hamilton website after login found at: 
                                        # https://cloud.hamiltoniot.com/api
                                        # simply copy paste your API key into the d_auth variable as
                                        # as a string.



# --------------------------------------------------------------------------------------------------
# Perform the request and access the data returned

req = requests.get("https://" + api_type + ".hamiltoniot.com/v1/data/rollup/" + d_sensor, 
                   params = {"from": d_from, "to": d_to, "millis": d_millis, "rollup": d_rollup},
                   headers = {"accept": d_header, "Authorization": d_auth})

print "URL generated by request:\n" + req.url + "\n"

res_json = req.json()               # get the JSON response out of the response

if(req.status_code != 200):         # check for successful GET request
    print "Server response code: " + str(req.status_code) + "\n"
    print "Server response: " + res_json[u"message"]
    exit(0)


print "JSON keys:\n" + str(res_json.keys()) + "\n"

print "Metadata about device (Note: u'results' skipped):"
for k in res_json.keys():
    if(k != u"results"):
        print str(k) + ((14 - len(str(k)))*" ") + ": " + str(res_json[k])   # can access data like 
print                                                                       # a simple python
                                                                            # dictionary object



# --------------------------------------------------------------------------------------------------
# now we access the sensor data of the requested sensor

print "Keys available in u'results':\n" + str(res_json[u"results"].keys()) + "\n"

# accessing the air temperature data from the sensor 
print "Keys available in u'results' -> u'air_temp':\n" + \
       str(res_json[u'results'][u'air_temp'].keys()) + "\n" # one should note at this point that
                                                            # each data recorded has 5 keys and
                                                            # shall be explained below
                                                            
# counts   : number of data points recorded during the requested rollup
# means    : the mean value of all the data recorded in a rollup
# maximums : the maximum value of recorded in the rollup
# minimums : the minimum value of recorded in the rollup
# times    : the time at which a rollup epoch occured
    
print "Sensor data contained in each key taken from u'air_temp':"
for k in res_json[u'results'][u'air_temp'].keys():
    print "u'" + k + "':"
    print res_json[u'results'][u'air_temp'][k]
    print

# at this point data can simply be accessed by referencing into each list in standard python fashion
print "42nd mean air temperature recorded: " + str(res_json[u'results'][u'air_temp'][u'means'][42])
    

