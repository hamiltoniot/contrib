/* -------------------------------------------------------------------------------------------------

 This program is a simple play around with the Hamilton API from a Go perspective. This file 
 primarily deals with building an API GET request to fetch sensor data and use it.

 Tested On: go version go1.6.2 linux/amd64 (Ubuntu 16.04)
 Libraries: fmt, bytes, net/http, io/ioutils, os   (These should come pre-installed with Go)

 Created by: Alan Herbert (hamilton@eskerfall.com)

------------------------------------------------------------------------------------------------- */

// -------------------------------------------------------------------------------------------------
// Packages and imports
// -------------------------------------------------------------------------------------------------

package main

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

// general hamilton device struct
type hamiltonDevice struct {
    DeviceId string `json:"deviceId"`
    More bool `json:"more"`
    NextFrom string `json:"nextFrom"`
    RollupSeconds int `json:"rollupSeconds"`
    Name string `json:"name"`
    Site string `json:"site"`
    Tier string `json:"_tier"`
    DeviceModel string `json:"_model"`
    DeviceType string `json:"_type"`
    Results map[string]int `json:"results"`
}



// -------------------------------------------------------------------------------------------------
// Globals
// -------------------------------------------------------------------------------------------------

var d_sensor = "01072D"

var d_from   = "2018-01-07T01:00:00-02:00"
var d_to     = "2018-01-07T02:00:00-02:00"

var d_millis = "true"

var d_rollup = "5m"

var d_limit  = "1000"

var d_header = "application/json"
var d_auth   = ""



// -------------------------------------------------------------------------------------------------
// Functional code body
// -------------------------------------------------------------------------------------------------

// -------------------------------------------------------------------------------------------------
// convert JSON response to a hamiltonDevice struct
/*
func getDevices(body []byte) (*hamiltonDevice, error) {
    var hamDev = new(hamiltonDevice)
    err:= json.Unmarshal(body, &hamDev)
    
    return hamDev, err

}
*/

// -------------------------------------------------------------------------------------------------
// Main function that does all the dirty work

func main() {
    // as the request to be made needs to be built up, we create a client to perform the request
    // for us.
    
    cli := &http.Client{}
    
    // generate a new GET request to the with the required data
    var urlBuffer bytes.Buffer
    urlBuffer.WriteString("https://devapi.hamiltoniot.com/v1/data/rollup/")
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
    
    resBody, err := ioutil.ReadAll(res.Body)
    
    var hamDev = new(hamiltonDevice)
    err = json.Unmarshal([]byte(resBody), &hamDev)
    
    fmt.Printf(">>>%s<<<\n", hamDev.DeviceId)
    
    if err != nil {
        fmt.Printf("%s", err)
        os.Exit(1)
    }
    fmt.Printf("%s\n", string(resBody))
    
}
