import json
import boto3
import os
from botocore.vendored import requests
from base64 import b64encode
import decimalencoder
import datetime
from itertools import groupby

client = boto3.client('ssm')

def get_secret(key):
	resp = client.get_parameter(
		Name=key,
		WithDecryption=True
	)
	return resp['Parameter']['Value']

def atco(event, context):
	statusCode = 200

	api_user = get_secret('api_user')
	api_password = get_secret('api_password')
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

	response = {
        "headers": {
            "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
            "Access-Control-Allow-Credentials" : True, # Required for cookies, authorization headers with HTTPS
            "Cache-Control" : "public, max-age=60"
        },
        "statusCode": statusCode,
        "body": json.dumps(jiraResponse, cls=decimalencoder.DecimalEncoder)
    }

	return response

def contractNotices(event, context):
	statusCode = 200

	headers = {
        'content-type': 'application/json'
    }
	starttime = datetime.datetime.now().strftime("%Y-01-01T00:00:00Z")
	currenttime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

	response = requests.get(os.environ['cnapibase']+starttime+"/"+currenttime,headers=headers)
	jsonResponse = json.loads(response.content.decode('utf8'))

	cnResponse = []
	found = True

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

	apiResponse = {}
	apiResponse['key']=uniquekeys
	apiResponse['count']=groups

	response = {
        "headers": {
            "Access-Control-Allow-Origin" : "*", # Required for CORS support to work
            "Access-Control-Allow-Credentials" : True, # Required for cookies, authorization headers with HTTPS
            "Cache-Control" : "public, max-age=60"
        },
        "statusCode": statusCode,
        "body": json.dumps(apiResponse, cls=decimalencoder.DecimalEncoder)
    }

	return response
