############################################################
# Name: sc_delete_scan_results.py                          #
# Description: Removes all scan results from               #
# SecurityCenter 5.x.                                      #
#                                                          #
# **DISCLAIMER**                                           #
# This script was designed for SecurityCenter 5.x using    #
# Python 2.7.  Please make sure all variables at the       #
# bottom of this script are filled in prior to running.    #
#                                                          #
#                                                          #
# INSTRUCTIONS FOR USE:                                    #
# This script uses 'requests' and 'urllib3', please make   #
# sure those are installed on your system. You can install #
# these using pip.  To install pip, download and run this  #
# script: https://bootstrap.pypa.io/get-pip.py             #
# Once pip has been installed, run:                        #
# pip install requests                                     #
#                                                          #
# 1. Fill in all variables listed below (currently the     #
# variables are set with dummy values).                    #
# 2. Run the script.  This will delete ALL scan results    #
# This CANNOT be undone.                                   #
# 3. Running this script as the 'admin' user will          #
# delete ALL scan results that are manageble by the admin. #
# THIS CANNOT BE UNDONE!!                                  #
#                                                          #
# Version 1.1 		                                       #
# Created by: Chad D                                       #
############################################################

import requests
import json
import sys
requests.packages.urllib3.disable_warnings()

# Fill in these variables
url = "https://"
username = ""
password = ""

# Do not fill in these variables
token = ''
cookie = ''

def build_url(restCall):
	return '{0}{1}'.format(url, restCall)

def connect(method, resource, data=None, headers=None, cookies=None):
	if headers is None:
		headers = {'Content-type': 'application/json',
					'X-SecurityCenter': str(token)}					
	if data is not None:
		data = json.dumps(data)
	
	if method == "POST":
		r = requests.post(build_url(resource), data=data, headers=headers, cookies=cookie, verify=False)
	elif method == "DELETE":
		r = requests.delete(build_url(resource), data=data, headers=headers, cookies=cookie, verify=False)
	elif method == "GET":
		r = requests.get(build_url(resource), data=data, headers=headers, cookies=cookie,verify=False)
	
	if r.status_code != 200:
		e = r.json()
		print e['error_msg']
		sys.exit()
		
	return r


def login (uname, pword):
	# Logs into SecurityCenter and retrieves our token and cookie.
	headers = {'Content-Type':'application/json'}
	login = {'username': uname, 'password':pword}
	data = connect('POST', '/rest/token', data=login, headers=headers)
	cookie = data.cookies
	token = data.json()['response']['token']
	return (cookie, token)

def scanResults():
	# Retrieves a list of scan result IDs and stores them in a list.
	scanResults = []
	data = connect('GET', '/rest/scanResult')
	results = data.json()['response']['manageable']
	if not results:
		print "There are no manageable scan results to delete."
	else:
		for i in results:
			scanResults.append(i['id'])
	return scanResults

def delete_scan_results():
	# Loops through our list of scan IDs and deletes each one.
	for x in result_list:
		data =  connect('DELETE', '/rest/scanResult/{0}'.format(x))
		print "Scan result {0} deleted.".format(x)

if __name__ == '__main__':
	print "Logging in..."
	cookie, token = login(username, password)
	print "Gathering scan result IDs.."
	result_list = scanResults()
	delete_scan_results()
