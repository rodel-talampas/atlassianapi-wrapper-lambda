import json
import boto3
import os
from botocore.vendored import requests
from base64 import b64encode
import xmltodict
import decimalencoder
import datetime
from itertools import groupby

if __name__ == "__main__":

    headers = {
        'content-type': 'application/json'
    }
    print(datetime.datetime.now())
    starttime = datetime.datetime.now().strftime("%Y-01-01T00:00:00Z")
    currenttime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    # starttime = datetime.datetime.now().strftime("2018-01-31T00:00:00Z")
    # currenttime = datetime.datetime.now().strftime("2018-02-01T23:23:59Z")
    response = requests.get(os.environ['cnapibase']+starttime+"/"+currenttime,headers=headers)
    jsonResponse = json.loads(response.content.decode('utf8'))

    cnResponse = []
    found = True
    #
    # print(starttime)
    # print(currenttime)

    #
    # for release in jsonResponse['releases']:
    #     contract = []
    #     contract.append(release['date'][0:7])
    #     contract.append(release['contracts'][0]['id'])
    #     cnResponse.append(contract)

    while found:
        for release in jsonResponse['releases']:
            contract = []
            contract.append(release['date'][0:7])
            contract.append(release['contracts'][0]['id'])
            cnResponse.append(contract)
        found = jsonResponse.get('links') != None and jsonResponse['links'].get('next') != None
        if found:
            nexturl = jsonResponse['links']['next']
            response = requests.get(nexturl,headers=headers)
            jsonResponse = json.loads(response.content.decode('utf8'))

    groups = []
    uniquekeys = []

    def datekey(val):
        return val[0]

    cnResponse = sorted(cnResponse,key=datekey)
    for k, g in groupby(cnResponse, key=datekey):
        groups.append(len(list(g)))
        uniquekeys.append(k)

    print(groups)
    print(uniquekeys)
    print(datetime.datetime.now())
