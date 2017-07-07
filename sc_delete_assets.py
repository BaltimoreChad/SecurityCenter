############################################################
# Name: sc_delete_assets.py                                #
# Description: Removes all managed assets from             #
# SecurityCenter 5.x.                                      #
#                                                          #
# **DISCLAIMER**                                           #
# This script was designed for SecurityCenter 5.x using    #
# Python 3.6.  Please make sure all variables at the       #
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
# Version 1.5		                                    #
# Created by: Chad D                                       #
############################################################


import json
import re
import sys

import requests

requests.packages.urllib3.disable_warnings()


class SecurityCenterAPI(object):
    """
    Class to handle our SecurityCenter API calls.
    """

    def __init__(self, username: str, password: str, url: str):
        self.username = username
        self.password = password
        self.url = url
        self.cookie = None
        self.token = None
        self.assets = []

    def build_url(self, resource):
        """
        Formats the SC URL with the requested resource.
        """
        return '{0}{1}'.format(self.url, resource)

    def connect(self, method: str, resource: str, data: dict = None, headers: dict = None):
        """ The connect method is used to connect to SC and pass our API calls."""
        if headers is None:
            headers = {'Content-type': 'application/json',
                       'X-SecurityCenter': str(self.token)}
        if data is not None:
            data = json.dumps(data)

        if method == "POST":
            resp = requests.post(self.build_url(resource), data=data, headers=headers, cookies=self.cookie,
                                 verify=False)
        elif method == "DELETE":
            resp = requests.delete(self.build_url(resource), data=data, headers=headers, cookies=self.cookie,
                                   verify=False)
        elif method == 'PATCH':
            resp = requests.patch(self.build_url(resource), data=data, headers=headers, cookies=self.cookie,
                                  verify=False)
        else:
            resp = requests.get(self.build_url(resource), data=data, headers=headers, cookies=self.cookie,
                                verify=False)

        if resp.status_code != 200:
            e = resp.json()
            sys.exit(e['error_msg'])

        if resp.headers.get('set-cookie') is not None:
            match = re.findall("TNS_SESSIONID=[^,]*", resp.headers.get('set-cookie'))
            self.cookie = match[1]

        return resp

    def login(self):
        """
        Logs into SecurityCenter and retrieves our token and cookie. We create a separate header here since we do not
        have a X-SecurityCenter token yet.
        """
        headers = {'Content-Type': 'application/json'}
        login = {'username': self.username, 'password': self.password}

        # We use the connect function and pass it a POST method, /rest/token resource,
        # and our login credentials as data.  We also pass our headers from above for this function.
        data = self.connect('POST', '/rest/token', data=login, headers=headers)

        # We can pull the cookie out of our data object and store it as a variable.
        self.cookie = data.cookies

        # We can alo pull our token out from the returned data as well.
        self.token = data.json()['response']['token']
        return self.cookie, self.token

    def get_assets(self):
        """
        Queries for a list of manageable assets for the currently in user.
        :return list assets:   A list of manageable assets for the current user.
        """
        # Initiate an empty asset list.
        assets = []

        # Use the connect function with a GET method and /rest/asset resource.
        data = self.connect('GET', '/rest/asset')

        # Store the manageable assets in the results variable.
        results = data.json()['response']['manageable']

        # If results is empty, there are no manageable assets and the script exits.
        if not results:
            sys.exit("This user has no managed assets.")
        else:
            # For each asset in our results file, append the asset ID to our asset list.
            for i in results:
                assets.append(i['id'])
        self.assets = assets
        return assets

    def delete_assets(self):
        # Loops through our list of assets and deletes each one.
        for asset in self.assets:
            data = self.connect('DELETE', '/rest/asset/{0}'.format(asset))
            print("Asset {0} deleted.".format(asset))
        print("All managed assets have been deleted.")


if __name__ == '__main__':

    # Fill in these variables
    url = ""
    username = ""
    password = ""
    yes = set(['yes', 'y', 'ye', ''])
    no = set(['no', 'n'])

    print("Logging in...")
    # This calls the login function and passes it your credentials, no need to modify this.
    sc = SecurityCenterAPI(url=url, username=username, password=password)
    cookie, token = sc.login()
    print("Gathering assets...")
    sc.get_assets()
    confirm = input("This will delete ALL assets that are managed by the current user.  "
                    "Are you sure you want to proceed? [y/n]: ")
    if confirm in yes:
        sc.delete_assets()
    else:
        sys.exit('Assets will not be deleted.  Exiting...')
