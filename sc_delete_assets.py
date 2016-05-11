############################################################
# Name: sc_delete_assets.py                                #
# Description: Removes all managed assets from             #
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
# 2. Run the script.  This will delete ALL managed assets  #
# This CANNOT be undone.                                   #
#                                                          #
# Version 1.0 		                                   #
# Created by: Chad D                                       #
############################################################   

import requests
import json
import sys
requests.packages.urllib3.disable_warnings()

# Fill in these variables
url = ""
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

def get_assets():
	# Retrieves a list of assets and stores them in a list.
	assets = []
	data = connect('GET', '/rest/asset')
	results = data.json()['response']['manageable']
	if not results:
	  sys.exit("There are no assets to delete.")
	else:
		for i in results:
			assets.append(i['id'])
	return assets

def delete_assets():
	# Loops through our list of assets and deletes each one.
	for x in asset_list:
		data =  connect('DELETE', '/rest/asset/{0}'.format(x))
		print "Asset {0} deleted.".format(x)
	print "All managed assets have been deleted."

if __name__ == '__main__':
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    print "Logging in..."
    cookie, token = login(username, password)
    print "Gathering assets..."
    asset_list = get_assets()
    confirm = raw_input("This will delete ALL assets that are managed by the current user.  Are you sure you want to proceed? [y/n]: ")
    if confirm in yes:
        delete_assets()
    else:
        sys.exit('Assets will not be deleted.  Exiting...')
