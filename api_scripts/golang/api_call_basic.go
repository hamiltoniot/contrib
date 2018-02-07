/* -------------------------------------------------------------------------------------------------

 This program is a simple play around with the Hamilton API from a Go perspective. This file 
 primarily deals with building an API GET request to fetch sensor data and use it.

 Tested On: go version go1.6.2 linux/amd64 (Ubuntu 16.04)
            go version go1.9.3 windows/amd64 (Windows 10 (Version 1709, Build 16299.192))
 Libraries: fmt, bytes, encoding/json, net/http, io/ioutils, os   
            Note: These should come pre-installed with Go

 Created by: Alan Herbert (hamilton@eskerfall.com)

------------------------------------------------------------------------------------------------- */

// -------------------------------------------------------------------------------------------------
// Packages and imports
// -------------------------------------------------------------------------------------------------

// -------------------------------------------------------------------------------------------------
// packages
package main



// -------------------------------------------------------------------------------------------------
// imports
import (
    "fmt"
    "bytes"
    "encoding/json"
    "net/http"
    "io/ioutil"
    "os"
    )



// -------------------------------------------------------------------------------------------------
// Structs
// -------------------------------------------------------------------------------------------------

// -------------------------------------------------------------------------------------------------
// results data struct
type hamiltonDeviceData struct {
    Times []int64 `json:"times"`
    Maximums []float64 `json:"maximums"`
    Means []float64 `json:"means"`
    Minimums []float64 `json:"minimums"`
    Counts []int64 `json:"counts"`
}



// -------------------------------------------------------------------------------------------------
// results field struct
type hamiltonDeviceResults struct {
    AccX hamiltonDeviceData  `json:"acc_x"`
    AccY hamiltonDeviceData `json:"acc_y"`
    AccZ hamiltonDeviceData `json:"acc_z"`
    AirHumidity hamiltonDeviceData `json:"air_hum"`
    AirRelativeHumidity hamiltonDeviceData `json:"air_rh"`
    AirTemp hamiltonDeviceData `json:"air_temp"`
    Lux hamiltonDeviceData `json:"lux"`
    MagneticX hamiltonDeviceData `json:"mag_x"`
    MagneticY hamiltonDeviceData `json:"mag_y"`
    MagneticZ hamiltonDeviceData `json:"mag_z"`
}



// -------------------------------------------------------------------------------------------------
// general hamilton device struct
type hamiltonDevice struct {
    DeviceId string `json:"deviceId"`
    More bool `json:"more"`
    NextFrom string `json:"nextFrom"`
    RollupSeconds int64 `json:"rollupSeconds"`
    Name string `json:"name"`
    Site string `json:"site"`
    Tier string `json:"_tier"`
    DeviceModel string `json:"_model"`
    DeviceType string `json:"_type"`
    Results hamiltonDeviceResults `json:"results"`
}



// -------------------------------------------------------------------------------------------------
// Globals
// -------------------------------------------------------------------------------------------------

var d_sensor = ""                   // for example: "01072D"

var d_from   = ""                   // start time of data to be fetched.
var d_to     = ""                   // end time of data to be fetched (this also works in unix
                                    // seconds, but this code sticks to RFC 3339).
                                    // for example with time zone: "2018-01-15T01:00:00-02:00"

var d_millis = "true"               // returns times in milliseconds, setting to false returns time
                                    // in nanoseconds (javascript sometimes battles with this
                                    // accuracy).
                                    // this has been set to "true" as a default value.

var d_rollup = "5m"                 // sensor data placed into 5 minute buckets.
                                    // this has been set to "5m" as a default value.

var d_limit  = "1000"               // limit number of data points to respond with in a request.
                                    // this has been set to "1000" as a default value.

var d_header = "application/json"   // required header information.
var d_auth   = ""                   // auth key required in header too.
                                    // this can be obtained from the "API Access" tab on the 
                                    // Hamilton website after login found at: 
                                    // https://cloud.hamiltoniot.com/api
                                    // simply copy paste your API key into the d_auth variable as
                                    // as a string.



// -------------------------------------------------------------------------------------------------
// Functional code body
// -------------------------------------------------------------------------------------------------

// -------------------------------------------------------------------------------------------------
// Main function that does all the dirty work. Settled on this style cause its easier to read from
// top to bottom than bouncing between functions.

func main() {
    // as the request to be made needs to be built up, we create a client to perform the request
    // for us.
    
    cli := &http.Client{}
    
    // generate a new GET request to the with the required data
    var urlBuffer bytes.Buffer
    urlBuffer.WriteString("https://api.hamiltoniot.com/v1/data/rollup/")
    urlBuffer.WriteString(d_sensor)
    
    req, err := http.NewRequest("GET", urlBuffer.String(), nil)
    
    if err != nil {             // simple error check and print
        fmt.Printf("%s", err)
        os.Exit(1)
    }
    
    // set header information
    req.Header.Set("accept", d_header)
    req.Header.Set("Authorization", d_auth)
    
    // add parameters to the get request
    params := req.URL.Query()
    
    params.Add("from", d_from)
    params.Add("to", d_to)
    params.Add("limit", d_limit)
    params.Add("millis", d_millis)
    params.Add("rollup", d_rollup)
    
    req.URL.RawQuery = params.Encode()  // encode parameters into standard URL format
    
    // use our client to perform our GET request we built
    res, err := cli.Do(req)

    if err != nil {             // simple error check and print
        fmt.Printf("%s", err)
        os.Exit(1)
    }
    
    // we pull the body out of the response from the server
    resBody, err := ioutil.ReadAll(res.Body)
    
    if err != nil {             // simple error check and print
        fmt.Printf("%s", err)
        os.Exit(1)
    }
    
    
    fmt.Printf("Response body:\n%s\n\n", string(resBody))
    
    // as we know that the response body is made up of only JSON, we can pass it directly into a 
    // JSON decoder. this requires us to create our own object, defined in the struct 
    // hamiltonDevice, and pass its memory location to the decoder so that it can be written to.
    // Note: hamiltonDevice makes use of hamiltonDeviceResults and hamiltonDeviceData in order to
    //       to fully traverse the nested JSON datastructures.
    var hamDev = new(hamiltonDevice)
    err = json.Unmarshal([]byte(resBody), &hamDev)
    
    // at this point all the data responded to from the hamiltoniot database is accessible through
    // the hamDev variable. each can be accessed using the dot '.' operator. for example:
    fmt.Printf("Device metadata:\n")
    fmt.Printf("Device ID .... : %s\n", hamDev.DeviceId)
    fmt.Printf("More ......... : %t\n", hamDev.More)
    fmt.Printf("Next From .... : %s\n", hamDev.NextFrom)
    fmt.Printf("Rollup Seconds : %d\n", hamDev.RollupSeconds)
    fmt.Printf("Name ......... : %s\n", hamDev.Name)
    fmt.Printf("Site ......... : %s\n", hamDev.Site)
    fmt.Printf("Tier ......... : %s\n", hamDev.Tier)
    fmt.Printf("Device Model . : %s\n", hamDev.DeviceModel)
    fmt.Printf("Device Type .. : %s\n\n", hamDev.DeviceType)

    // to access something a little deeper we can extend the use of our dot operator '.'
    fmt.Printf("Mean air temperature at time %d was %f\n", hamDev.Results.AirTemp.Times[42], 
               hamDev.Results.AirTemp.Means[42])
}
