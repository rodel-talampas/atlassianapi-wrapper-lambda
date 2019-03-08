import json
import boto3
import os
from botocore.vendored import requests
from base64 import b64encode
import xmltodict
import decimalencoder

api_user = 'apiuser@gruden.com'
api_password = 'GrudenFun987!'
plainUserPass="{0}:{1}".format(api_user,api_password)
userAndPass = b64encode(str.encode(plainUserPass)).decode("ascii")

headers = {
    'content-type': 'application/json'
}

body = json.dumps({
    "username": api_user,
    "password": api_password
})
print(os.environ['jirabase']+os.environ['authurl'])
response = requests.post(os.environ['jirabase']+os.environ['authurl'],data=body,headers=headers)
jsonResponse = json.loads(response.content.decode('utf8').replace("'",'"'))

print(jsonResponse['session'])


if __name__ == "__main__":

    headers = {
        'content-type': 'application/json',
        'cookie': "{0}={1}".format(jsonResponse['session']['name'],jsonResponse['session']['value'])
    }

    body = json.dumps({
        "jql":"project=ATCO and status in ('In Progress','Open') order by priority desc, duedate asc"
    })
    response = requests.post(os.environ['jirabase']+os.environ['searchurl'],data=body,headers=headers)
    jsonResponse = json.loads(response.content.decode('utf8'))

    # print(jsonResponse)

    jiraResponse = []

    for ticket in jsonResponse['issues']:
        issue = {}
        issue['id'] = ticket['id']
        issue['key'] = ticket['key']
        issue['type'] = ticket['fields']['issuetype']['name']
        issue['priority'] = ticket['fields']['priority']['name']
        issue['status'] = ticket['fields']['status']['name']
        issue['description'] = ticket['fields']['description']

        jiraResponse.append(issue)

    print(jiraResponse)
