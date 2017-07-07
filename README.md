## Synopsis

A few different scripts that I've put together over the last couple of years that work with Tenable's SecurityCenter.  This scripts are by no means perfect but they should offer a decent starting point.

## Brief Description of Scripts

`auto_sc_config.py` - This script was written in Python2.7 and could probably use some cleaning up.  Essentially, you fill in the variables at the bottom of the page and then run the script.  The script will go through all of the installation prompts for you.

`sc_delete_assets.py` - Another script that was written in Python2.7 that needs to be converted to Python 3.  A quick script thrown together that deletes all assets manageable by the current user.

`sc_delete_scan_results.py` - The last of the Python2.7 scripts, this one also needs to be converted to Python 3.  This script will delete all scan results.  Running this script as 'admin' will delete **ALL** scan results manageable by the admin user.

`sc_api_template.py` - A quick SecurityCenter API Template written in Python 3 that works on the latest release of SecurityCenter (as of this writing that is 5.5).  I've left some samples coded in just for reference.

## Contributors

Feel free to submit pull requests to this project and make it your own.  I can be reached on twitter at http://www.twitter.com/programmerchad
