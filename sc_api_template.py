############################################################
# Name: sc_api_template.py                                 #
# Description: SecurityCenter 5 API Template.              #
#                                                          #
# **DISCLAIMER**                                           #
# This script was designed for SecurityCenter 5.x using    #
# Python 3.x.  Please make sure all variables at the       #
# bottom of this script are filled in prior to running.    #
#                                                          #
#                                                          #
# INSTRUCTIONS FOR USE:                                    #
# This script uses 'requests' and 'urllib3', please make   #
# sure those are installed on your system. You can install #
# these using pip.  To install pip, download and run this  #
# script: https://bootstrap.pypa.io/get-pip.py             #
# Once pip has been installed, run:                        #
# pip3 install requests                                    #
#                                                          #
# This script is a shell of a Python 3 SecurityCenter API  #
# script.  It is up to you, the user, to create you own    #
# functions from here.  This should handle any request you #
# come across in the API.  I've left one function in the   #
# script, that is currently commented out, for reference.  #
# Uncomment the get_assets function to retrieve the asset  #
# IDs for all manageable assets for the current user.      #
#                                                          #
# 1. Fill in all variables listed below (currently the     #
# variables are set with dummy values).                    #
# 2. Use Firebug or some other method and create your      #
# own API functions.                                       #
# 3. For some examples, check out my github:               #
# https://github.com/BaltimoreChad                         #
# Version 1.0 		                                   #
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
	elif method == 'PATCH':
		r = requests.patch(build_url(resource), data=data, headers=headers, cookies=cookie, verify=False)
	else:
		r = requests.get(build_url(resource), data=data, headers=headers, cookies=cookie, verify=False)

	if r.status_code != 200:
		e = r.json()
		print(e['error_msg'])
		sys.exit()

	return r


def login (uname, pword):
	# Logs into SecurityCenter and retrieves our token and cookie.
	# We create a seperate header here since we do not have a X-SecurityCenter token yet.
	headers = {'Content-Type':'application/json'}
	login = {'username': uname, 'password':pword}

	# We use the connect function and pass it a POST method, /rest/token resource,
	# and our login credentials as data.  We also pass our headers from above for this function.
	data = connect('POST', '/rest/token', data=login, headers=headers)

	# We can pull the cookie out of our data object and store it as a variable.
	cookie = data.cookies

	# We can alo pull our token out from the returned data as well.
	token = data.json()['response']['token']
	return (cookie, token)

# ------- UNCOMMENT THE CODE BELOW TO ENABLE THE FUNCTION.  THIS WAS LEFT IN FOR REFERENCE. ------- #
# -------    LINES WITH '##' ARE COMMENTS, YOU DO NOT NEED TO UNCOMMENT THOSE LINES.        ------- #
# def get_assets():
# 	# Initiate an empty asset list.
# 	assets = []
#
# 	# Use the connect function with a GET method and /rest/asset resource.
# 	data = connect('GET', '/rest/asset')
#
# 	# Store the manageable assets in the results variable.
# 	results = data.json()['response']['manageable']
#
# 	# If results is empty, there are no manageable assets and the script exits.
# 	if not results:
# 		sys.exit("This user has no managed assets.")
# 	else:
# 		# For each asset in our results file, append the asset ID to our asset list.
# 		for i in results:
# 			assets.append(i['id'])
# 	return assets

if __name__ == '__main__':
	print("Logging in...")
	# This calls the login function and passes it your username and password, no need to modify this.
	cookie, token = login(username, password)

	# You can call your functions from above here.
	# You can change the next print statement to match whatever your function is doing ("Gathering scans.."/etc).
	# Right now this just prints your cookie and token so you can confirm the login function worked on your system.
	print("This is a template for creating SecurityCenter API Python scripts....")
	print(cookie, token)

	# ------- UNCOMMENT THE CODE BELOW TO GATHER YOUR MANAGED ASSETS.  THIS WAS LEFT IN FOR REFERENCE. ------- #
	# -------    LINES WITH '##' ARE COMMENTS, YOU DO NOT NEED TO UNCOMMENT THOSE LINES.        ------- #
	# # Call our get_assets() function and stores our asset IDs as assetList
	# assetList = get_assets()
	#
	# # For each ID in assetList, print it to screen.
	# for id in assetList:
	# 	print("Asset ID: "+id)
