import sys
import requests
import requests_html
import time
import datetime
import random
import logging
import re # RegEx
import urllib3
from termcolor import colored
from config import *

# Start logging runtime of this single run
log_starttime = datetime.datetime.now()

# Create default logger
if(debug):
    logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.DEBUG)
    logging.debug("Debug mode is turned on")
else:
    logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

# Initialize counters for logger statistics
cntLogger = {
    "warning": 0,
    "error": 0,
    "critical": 0
}

# Dont modify these counters/flags
cntDeadPage = 0
cntExceptionGET = 0
cntExceptionPOST = 0
dnsworking = True

# Disable SSL-Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL for giveaways (giveawayID missing)
url_ga = "https://astats.astats.nl/astats/Giveaway.php?GiveawayID="
url_ga_backup = "http://31.151.215.13/astats/Giveaway.php?GiveawayID="

# URL for profile page (steamID missing)
url_profile_ga = "https://astats.astats.nl/astats/User_Info.php?SteamID64="
url_profile_ga_backup = "http://31.151.215.13/astats/User_Info.php?SteamID64="

# URL for crawlerqueue
url_crawler = "https://astats.astats.nl/astats/Stats.php"
url_crawler_backup = "http://31.151.215.13/astats/Stats.php"

# Get account name from first console argument
account_name = sys.argv[1]

# Read all last used giveaway IDs from txt file
with open("lastIDs.txt", "r") as file:
    input = file.readlines()

# Find corresponding giveaway ID for this account
id = -1
i = 0 
while(i < len(input)):
    input[i] = input[i].rstrip()
    str_split = input[i].split(":")
    if (str_split[0] == account_name):
        id = int(str_split[1])
    i += 1
if(id == -1):
    logging.critical("Corrupted lastIDs.txt file!")
    cntLogger["critical"] += 1
    sys.exit()

# Check at the end, if any progress were made
backupID = id

# Default Cookie
cookies_ga = {
    "COOKIE_NAME": accounts_cookie[account_name],
    "cookieconsent_dismissed": "yes",
    "PHPSESSID": accounts_phpID[account_name]
}

# Modify Header for GET and POST (e.g. replace "python-requests/.." User-Agent)
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3", 
    "Connection": "keep-alive"
}

# Payload for joining the giveaway
payload_ga = {
    "Comment": "",
    "JoinGiveaway": "Join"
}

# Initialize counters for the statistics
cntJoined = 0
cntfailed = {
    "joined_already": 0,
    "game_owned": 0,
    "giveaway_ended": 0,
    "invalid_cookie": 0,
    "group_missing": 0,
    "max_entries": 0,
    "not_published": 0,
    "not_started": 0,
    "unkown": 0
}

# Sessions for GET and POST requests
session_ga_post = requests.Session()
session_ga_get = requests_html.HTMLSession()

# Visit profile page before joining giveaways (this gets logged on the webserver)
logging.debug("Visiting profile page:")
try:
    profile_ga = session_ga_get.get(url_profile_ga + steam_id[account_name], cookies=cookies_ga, headers=header, verify=False)
except:
    dnsworking = False
    try:
        profile_ga = session_ga_get.get(url_profile_ga_backup + steam_id[account_name], cookies=cookies_ga, headers=header, verify=False)
    except:
        logging.critical("Visiting profile page failed")
        cntLogger["critical"] += 1
        sys.exit()

if(dnsworking):
    logging.debug("DNS is working.")
else:
    logging.warning("DNS is NOT working!")

# Check if initial GET request worked
if(not profile_ga.ok):
    logging.critical("Received HTTP status code: " + str(profile_ga.status_code))
    cntLogger["critical"] += 1
    sys.exit()

# Check mailbox
if(profile_ga.text.find("new message") > -1):
    logging.warning("You have " + re.search("You have (.*)!</a>", profile_ga.text).group(1) + "!")
    cntLogger["warning"] += 1

time.sleep(1)

# Check AStats crawler status for server load prediction
logging.debug("Checking AStats crawler:")
try:
    if(dnsworking):
        crawlerqueue = session_ga_get.get(url_crawler, cookies=cookies_ga, headers=header, verify=False)
    else:
        crawlerqueue = session_ga_get.get(url_crawler_backup, cookies=cookies_ga, headers=header, verify=False)
except:
    logging.critical("Checking AStats crawler failed")
    cntLogger["critical"] += 1
    sys.exit()

crawlerload = re.search("<br>(.*) user command(s)? (is|are) currently in the crawler queue.</li>", crawlerqueue.text)

time.sleep(1)

if(crawlerload == None): 
    logging.error("Error occurred while trying to access crawler load")
    cntLogger["error"] += 1
else:
    try:
        crawlerload = int(crawlerload.group(1).replace(" ", "").replace(".", ""))
        if(crawlerload > 99):
            logging.warning("Astats service is currently under heavy load, crawler queue lenght: " + str(crawlerload))
            cntLogger["warning"] += 1
    except:
        logging.error("Error occurred while trying to compute crawler load, value is " + str(crawlerload))
        cntLogger["error"] += 1

# Start searching for open giveaways
logging.debug("Starting main algorithm:")

while(True):
    if(cntLogger["critical"] > 0):
        logging.critical("Critical Error occurred!")
        break
	# GET request for giveaway page with specific id
    while(cntExceptionGET < thresholdExceptionGET):
        try:
            if(dnsworking):
                req_ga_get = session_ga_get.get(url_ga + str(id), cookies=cookies_ga, headers=header, verify=False)
            else:
                req_ga_get = session_ga_get.get(url_ga_backup + str(id), cookies=cookies_ga, headers=header, verify=False)
        except:
            cntExceptionGET += 1
            logging.warning("Failed GET request on ID [" + str(id) + "] - tried " + str(cntExceptionGET) + " time(s)")
            cntLogger["warning"] += 1
            time.sleep(1)
        else:
            cntExceptionGET = 0
            break
    if(cntExceptionGET >= thresholdExceptionGET):
        logging.critical("GET request failed " + str(cntExceptionGET) + " time(s)!")
        cntExceptionGET = 0
        break
    # Search for the navbar (Does the page/giveaway exist?)
    navbar = req_ga_get.html.find(".navbar-brand")
    # Search for button to join the giveaway (Is it possible to join the giveaway?)
    button = req_ga_get.html.find("[name=JoinGiveaway]")
    if(len(navbar) > 0):
        # Giveaway exists, reset counter for successively(!) requests resulting in a non existing page
        cntDeadPage = 0

        if(len(button) > 0):
            # Giveaway can be joined
            time.sleep(random.randint(1, 3))
            # POST request to join the giveaway
            while(cntExceptionPOST < thresholdExceptionPOST):
                try:
                    if(dnsworking):
                        req_ga_post = session_ga_post.post(url_ga + str(id), cookies=cookies_ga, headers=header, data=payload_ga, verify=False)
                    else:
                        req_ga_post = session_ga_post.post(url_ga_backup + str(id), cookies=cookies_ga, headers=header, data=payload_ga, verify=False)
                except:
                    cntExceptionPOST += 1
                    logging.warning("Failed POST request on ID [" + str(id) + "] - tried " + str(cntExceptionPOST) + " time(s)")
                    cntLogger["warning"] += 1
                    time.sleep(1)
                else:
                    cntExceptionPOST = 0
                    cntJoined += 1
                    logging.info("Joined giveaway [" + str(id) + "]")
                    break
            if(cntExceptionPOST >= thresholdExceptionPOST):
                logging.critical("POST request failed " + str(thresholdExceptionPOST) + " time(s)!")
                cntExceptionPOST = 0
                break
        else:
            # Giveaway can not be joined
            content_ga = req_ga_get.text
            message_ga = "Giveaway [" + str(id) + "] exists, but can't be joined. Reason: "
            if(content_ga.find("You have joined this giveaway already.") > -1):
                cntfailed["joined_already"] += 1
                logging.info(message_ga + "Giveaway already joined.")
            elif(content_ga.find("You already own the giveaway game.") > -1):
                cntfailed["game_owned"] += 1
                logging.info(message_ga + "Giveaway game already in steam library")
            elif(content_ga.find("This giveaway has ended.") > -1):
                cntfailed["giveaway_ended"] += 1
                logging.info(message_ga + "Giveaway ended.")
            elif(content_ga.find("You need to be logged in to participate in giveaways.") > -1):
                cntfailed["invalid_cookie"] += 1
                logging.critical(message_ga + "Cookie invalid!")
                cntLogger["critical"] += 1
                break
            elif(content_ga.find("not in the required group") > -1):
                cntfailed["group_missing"] += 1
                logging.warning(message_ga + "Group membership missing for " + re.search("Steam group member of (.*)</td>", content_ga).group(1))
                cntLogger["warning"] += 1
            elif(content_ga.find("aximum entries") > -1):
                cntfailed["max_entries"] += 1
                logging.info(message_ga + "Maximum entries reached.")
            elif(content_ga.find("This giveaway has not been published.") > -1):
                cntfailed["not_published"] += 1
                logging.info(message_ga + "Giveaway has not been published yet.")
            elif(content_ga.find("This giveaway has not yet started.") > -1):
                cntfailed["not_started"] += 1
                logging.info(message_ga + "This giveaway has not yet started.")
            else:
                cntfailed["unkown"] += 1
                logging.critical(message_ga + "Unknown reason!")
                cntLogger["critical"] += 1
                break

    else:
        # Giveaway does not exist
        if(cntDeadPage >= (thresholdDeadPage - 1)):
            # threshold reached
            logging.debug("Found non exisitng giveaway page with ID [" + str(id) + "]")
            # Check if there is some progress
            if(backupID <= id - 1 - cntDeadPage):
                logging.info("Reached last giveaway ID [" + str(id - 1 - cntDeadPage) + "]")
                # Store last ID (first not existing giveaway) in txt file
                i = 0 
                while(i < len(input)):
                    if(input[i].split(":")[0] == account_name):
                        input[i] = account_name + ":" + str(int(id - cntDeadPage)) + "\n"
                    else:
                        if(i < len(input) - 1):
                            input[i] += "\n"
                    i += 1
                with open("lastIDs.txt", "w") as file:
                    file.writelines(input)
            else:
                logging.info("No new giveaways have been added since last run.")
            break
        else:
            logging.debug("Found non exisitng giveaway page with ID [" + str(id) + "]")
            cntDeadPage += 1

    id += 1
    time.sleep(random.randint(1, 2))


# Manage global stats

# Add up all fail-counter
sumCntFailed = 0
for key in cntfailed:
    sumCntFailed += cntfailed[key]

# List respecting stats.txt layout containing all counters and stats
tempStats = [
    1, # increment by 1 for bot starting counter in stats file
    cntJoined, 
    sumCntFailed,
    cntfailed["joined_already"],
    cntfailed["game_owned"],
    cntfailed["giveaway_ended"],
    cntfailed["invalid_cookie"],
    cntfailed["group_missing"],
    cntfailed["max_entries"],
    cntfailed["not_published"],
    cntfailed["not_started"],
    cntfailed["unkown"]
    ]

# Read all old stats and save them temporary
with open("stats.txt", "r") as file:
    inputStats = file.readlines()

# Add all local counter values to the old stats
i = 0 
while(i < len(inputStats)):
    inputStats[i] = inputStats[i].split(":")[0] + ":" + str(tempStats[i] + int(inputStats[i].split(":")[1])) + "\n"
    i += 1

# Store new stats in txt file
with open("stats.txt", "w") as file:
        	file.writelines(inputStats)

# Run completed
if(cntJoined > 0):
    logging.info("Total amount of joined giveaways in this run: >> " + str(cntJoined) + " <<")
noIncidents = True

if(cntLogger["warning"] > 0):
    logging.info(colored("Warnings: " + str(cntLogger["warning"]), "yellow"))
    noIncidents = False
else:
    logging.info("Warnings: 0")

if(cntLogger["error"] > 0):
    logging.info(colored("Errors: " + str(cntLogger["error"]), "red"))
    noIncidents = False
else:
    logging.info("Errors: 0")

if(cntLogger["critical"] > 0):
    logging.info(colored("Critical Errors: " + str(cntLogger["critical"]), "red"))
    noIncidents = False
else:
    logging.info("Critical Errors: 0")

if(noIncidents):
    logging.info(colored("Bot successfully terminated.", "green"))
else:
    logging.info(colored("Bot terminated.", "red"))
    
log_endtime = datetime.datetime.now()
log_runtime = (log_endtime - log_starttime)
logging.info("Total runtime: " + str(log_runtime))