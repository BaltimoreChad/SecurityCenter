############################################################
# Name: autoSCConfig.py                                    #
# Description: Uses supplied information to configure      #
# SecurityCenter 5.x.                                      #
#                                                          #
# **DISCLAIMER**                                           #
# This script was designed for SecurityCenter 5.x using    #
# Python 2.7.  Please make sure all variables at the       #
# bottom of this script are filled in prior to running.    #
#                                                          #
#                                                          #
# INSTRUCTIONS FOR USE:   				   #
# This script uses 'requests' and 'urllib3', please make   #
# sure those are installed on your system. You can install #
# these using pip.                                         #
#                                                          #
# 1. Fill in all variables listed below (currently the     #
# variables are set with dummy values).                    #
# 2. Install the SecurityCenter 5 RPM.  Once installation  #
# is complete, start the service by running:               #
# service SecurityCenter start                             #
# 3. Next, run this python script from the command line.   #
# The script will use the given license key path and       #
# other defined variables to register the product.         #
# 4. Once the script is finished you can access your admin #
# account using your specified password or the 'secman'    #
# Security Manager account using 'password' for the        #
# password.  SecurityCenter will prompt you to change this.#
#                                                          #
# NOTE: This only registers a single Nessus scanner at     #
# this time.  Additional Nessus scanners, as well as LCE   #
# and PVS scanners must be added manually once setup is    #
# complete.                                                #
#                                                          #
# Version 1.0                                              #
############################################################      
    
import requests
import json
import sys
import urllib3
requests.packages.urllib3.disable_warnings()

class SecurityCenter:
	
	def __init__(self, server, verify_ssl=False):
		self.server = server
		self.verify = verify_ssl
		self.token = ''
		self.cookie = ''

	def login(self, username, password):
		# Our login function.  This will store and return our token 
		# value used later in the script.
		input = {'username': username, 'password': password}
		resp = self.connect('POST', 'token', input)

		if resp is not None:
			self.token = resp['token']

	def logout(self):
		# Destroys token forcing a logout.
		self.connect('DELETE', 'token')
		self.token = ''
		self.cookie = ''

	def connect(self, method, resource, data=None):
	
		headers = {
			'Content-Type': 'application/json',
		}

		if self.token != '':
			headers['X-SecurityCenter'] = self.token

		if self.cookie != '':
			headers['Cookie'] = self.cookie

		# Only convert the data to JSON if there is data.
		if data is not None:
			data = json.dumps(data)

		url = "https://{0}/rest/{1}".format(self.server, resource)
		
		# Our API calls (POST, PUT, DELETE, PATCH, GET)
		try:
			if method == 'POST':
				r = requests.post(url, data=data, headers=headers, verify=self.verify)
			elif method == 'PUT':
				r = requests.put(url, data=data, headers=headers, verify=self.verify)
			elif method == 'DELETE':
				r = requests.delete(url, data=data, headers=headers, verify=self.verify)
			elif method == 'PATCH':
				r = requests.patch(url, data=data, headers=headers, verify=self.verify)
			else:
				r = requests.get(url, params=data, headers=headers, verify=self.verify)
		
		# Checks for connection error and prints the error.
		except requests.ConnectionError, e:
			print str(e)
			return None
		
		if r.headers.get('set-cookie') is not None:
			self.cookie = r.headers.get('set-cookie')

		# Checks the data for a JSON response.  Returns none if no data exists.
		try:
			jsonData = r.json()
		except ValueError as e:
			print e
			return None

		# Throws an error message if the error code is not 0.
		if jsonData['error_code'] != 0:
			sys.exit(jsonData['error_msg'])

		# Returns the 'response' section of the JSON data.
		return jsonData['response']

	def upload(self, licenseKeyPath):

		headers = {
			'X-SecurityCenter': self.token,
			'Cookie': self.cookie
		}

		params = {}
		
		# Opens the file path and stores it as f
		f = open(licenseKeyPath,'r')
		
		# Sets files to include JSON data for the uploaded file.
		files = {'Filedata': f}

		url = "https://{0}/rest/file/upload".format(self.server)		

		print 'Uploading file {0}.'.format(licenseKeyPath)
		
		r = requests.post(url, headers=headers, params=params, files=files, verify=self.verify)
		
		# Prints JSON request data and response data.
		# These can be commented out if there is too much information displayed.
		print 'Request Data: {0}'.format(r.request.body)
		print 'Response Data: {0}'.format(r.content)

		# Make sure we have a JSON response. If not then return None.
		try:
			jsonData = r.json()
		except ValueError as e:
			print e
			return None

		# If the response error code is not 0, there is an error.
		if jsonData['error_code'] != 0:
			sys.exit(jsonData['error_msg'])

		# Return the filename given by SecurityCenter
		print "License has been uploaded successfully as {0}.".format(jsonData['response']['filename'])
		return jsonData['response']['filename']

	def applyLicense(self, fileName):
		# Applies the uploaded license file and registers SecurityCenter
		input = {"filename":fileName}
		print "Applying the license file."
		r = self.connect('POST', 'config/license/register', input)
		print "License was successfully applied."
	
	def registerNessus(self, nessusActivationCode):
		# Registers the provided Nessus activation code.
		print "Registering Nessus activation code..."
		input = {"activationCode":nessusActivationCode,
			"updateSite":"downloads.nessus.org",
			"type":"active"}
		r = self.connect('POST', '/config/plugins/register', input)
		
		# Checks if the activation code returned as 'invalid'.
		if ('Invalid' in r.values()):
			print "Invalid activation code.  This may be due to the code being in use or entered incorrectly."
		else:
			print "Nessus activation was successful."
	
	def setAdminPasswd(self, passwd):
		# Changes the admin password from 'admin' to the 
		# provided value.
		input = {"password":passwd}
		print "Changing administrator password..."
		r = self.connect('PATCH', '/user/1', input)
		print "Administrator password changed successfully."
		
	def addScanZone(self, name, range):
		# Adds scan zone using specified variables.
		input = {
		"id":"1",
		"name":name,
		"description":"",
		"ipList":range}
		print "Adding scan zone..."
		r = self.connect('POST', '/zone', input)
		print "Scan zone added successfully..."
		
	def addNessusScanner(self, scanZoneName, name, ip, nessusUN, nessusPW, port):
		# Adds Nessus scanner using the provided variables. 
		# Left more settings than needed in case other options
		# are needed (such as proxy).
		if port is "":
			port = 8834
		input={"id":"1",
		"name":name,
		"description":"",
		"ip":ip,
		"port":port,
		"useProxy":"false",
		"enabled":"true",
		"verifyHost":"false",
		"managePlugins":"true",
		"authType":"password",
		"username":nessusUN,
		"password":nessusPW,
		"admin":"false",
		"zones":
			[{
			"id":"1",
			"name":scanZoneName,
			"description":""
			}]
		}
		print "Adding Nessus scanner..."
		r = self.connect('POST', '/scanner', input)
		print "Nessus scanner added successfully."
	
	def addOrganization(self, orgName):
		# Adds organization using the provided variables. 
		input = {
		"id":"1",
		"name":orgName,
		"description":"",
		"zoneSelection":"auto_only"
		}
		print "Adding organization..."
		r = self.connect('POST', '/organization', input)
		print "Organization successfully added."
		
	def addRepository(self, orgName, repoName, repoIPRange):
		# Adds Repository using the provided variables. 
		input = {
		"name":repoName,
		"description":"",
		"dataFormat":"IPv4",
		"type":"Local",
		"trendingDays":"30",
		"trendWithRaw":"true",
		"ipRange":repoIPRange,
		"organizations":
			[{
			"id":1,
			"name":orgName,
			}]
		}
		print "Adding repository..."
		r = self.connect('POST', '/repository', input)
		print "Repository added successfully."
		
	def addSecurityManager(self, userName):
		# Creates Security Manager and assigns them to the freshly
		# created Organization.  Sets password to 'password' which
		# must be changed upon logging into the Security Manager.
		input = {
			"name":"",
			"description":"",
			"firstname":"Security",
			"lastname":"Manager",
			"username":"secman",
			"password":"password",
			"title":"Security Manager",
			"address":"",
			"city":"",
			"state":"",
			"country":"",
			"phone":"",
			"email":"",
			"fax":"",
			"authType":"tns",
			"orgID":1,
			"roleID":2,
			"mustChangePassword":"true"}
		print "Creating Security Manager ..."
		r = self.connect('POST', '/user', input)
		print "Security Manager created successfully."
		
if __name__ == '__main__':
	
	### MODIFY THE BELOW VARIABLES TO MATCH YOUR NEEDS. ###
	
	# SecurityCenter IP
	sc = SecurityCenter('127.0.0.1')
	
	# Path to your license key file.
	licenseKeyPath='/tmp/tenable-SecurityCenter-4.8-DEMO.key'
	
	# Nessus activation code
	nessusActivationCode=""
	
	# New administrator password
	newAdminPassword=""
	
	# Scan zone name.
	scanZoneName = "Test Scan Zone"
	
	# Scan Zone IP Range
	scanZoneRange = ""
	
	# Nessus scanner name
	nessusName = "Nessus Scanner"
	
	# Nessus IP Address
	nessusIP = ""
	
	# Nessus user name
	nessusUN = ""
	
	# Nessus password
	nessusPW = ""
	
	# Nessus port, this will default to 8834 if nothing is supplied.
	port = ""
	
	# Organization Name
	orgName = "Test Org"
	
	# Repository Name
	repoName = "Test Repo"
	
	# Repository IP Range
	repoIPRange = "0.0.0.0/0"
	
	# Security Manager user name
	securityManagerUN = "secman"

	### DO NOT MODIFY THE BELOW DATA ###
	sc.login('admin', 'admin')
	fileName = sc.upload(licenseKeyPath)
	sc.applyLicense(fileName)
	sc.registerNessus(nessusActivationCode)
	sc.setAdminPasswd(newAdminPassword)
	sc.addScanZone(scanZoneName, scanZoneRange)
	sc.addNessusScanner(scanZoneName, nessusName, nessusIP, nessusUN, nessusPW, port)
	sc.addOrganization(orgName)
	sc.addRepository(orgName, repoName, repoIPRange)
	sc.addSecurityManager(securityManagerUN)
	print "SecurityCenter is now configured."
	print "Logging out."
	sc.logout()
