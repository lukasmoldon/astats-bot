import sys
import requests
import requests_html
import time
import random
import logging
import re
import urllib3

# Create default logger
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

# Disable SSL-Warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL for giveaways
url_ga = "https://astats.astats.nl/astats/Giveaway.php?GiveawayID="

# URL for profile page
url_profile_ga = "http://astats.astats.nl/astats/User_Info.php?SteamID64="

# Get account name from first console argument
account_name = sys.argv[1]

# Read last ID for the account name from txt file
with open("lastIDs.txt", "r") as file:
    input = file.readlines()

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

# Steam64ID for diffrent accounts
steam_id = {
    "main": "", # Enter Steam profile ID here 
    "secondary": "" # Enter Steam profile ID here 
}

# COOKIE_NAME for different accounts
accounts_cookie = {
    "main": "", # Enter Cookie ID here 
    "secondary": "" # Enter Cookie ID here 
}

# PHPSESSID for different accounts
accounts_phpID = {
    "main": "", # Enter PHP Session ID here
    "secondary": "" # Enter PHP Session ID here
}

# Default Cookie
cookies_ga = {
    "COOKIE_NAME": accounts_cookie[account_name],
    "cookieconsent_dismissed": "yes",
    "PHPSESSID": accounts_phpID[account_name]
}

# Modify Header for GET and POST (remove "python-requests/.." User-Agent)
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

# Counters for the statistics
cntJoined = 0
cntfailed = {
    "joined_already": 0,
    "game_owned": 0,
    "giveaway_ended": 0,
    "invalid_cookie": 0,
    "group_missing": 0,
    "max_entries": 0,
    "not_published": 0,
    "unkown": 0
}

#Sessions for GET and POST requests
session_ga_post = requests.Session()
session_ga_get = requests_html.HTMLSession()

# Visit profile page before joining giveaways
profile_ga = session_ga_get.get(url_profile_ga + steam_id[account_name], cookies=cookies_ga, headers=header, verify=False)

# Check if HTTP request works
if(not profile_ga.ok):
    logging.critical("Received HTTP status code" + profile_ga.status_code)

while(True):
	# GET request for giveaway page
    req_ga_get = session_ga_get.get(url_ga + str(id), cookies=cookies_ga, headers=header, verify=False)
    # Search for the navbar -> Page exists
    navbar = req_ga_get.html.find(".navbar-brand")
    # Search for button to join the giveaway
    button = req_ga_get.html.find("[name=JoinGiveaway]")
    if(len(navbar) > 0):

        if(len(button) > 0):
            time.sleep(random.randint(1, 3))
            # POST request to join the giveaway
            req_ga_post = session_ga_post.post(url_ga + str(id), cookies=cookies_ga, headers=header, data=payload_ga, verify=False)
            cntJoined += 1
            logging.info("Joined giveaway [" + str(id) + "]")
        else:
            # Join button not found
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
                break
            elif(content_ga.find("not in the required group") > -1):
                cntfailed["group_missing"] += 1
                logging.warning(message_ga + "Group membership missing for " + re.search('Steam group member of (.*)</td>', content_ga).group(1))
            elif(content_ga.find("aximum entries") > -1):
                cntfailed["max_entries"] += 1
                logging.info(message_ga + "Maximum entries reached.")
            elif(content_ga.find("This giveaway has not been published.") > -1):
                cntfailed["not_published"] += 1
                logging.info(message_ga + "Giveaway has not been published yet.")
            else:
                cntfailed["unkown"] += 1
                logging.critical(message_ga + "Unknown reason!")

    else:
        logging.info("Reached last giveaway ID [" + str(id - 1) + "]")
        # Store last ID (first not existing giveaway) in txt file
        i = 0 
        while(i < len(input)):
            if(input[i].split(":")[0] == account_name):
                input[i] = account_name + ":" + str(id) + "\n"
            else:
                if(i < len(input) - 1):
                    input[i] += "\n"
            i += 1
        with open("lastIDs.txt", "w") as file:
        	file.writelines(input)
        break

    id += 1
    time.sleep(random.randint(1, 2))


# Manage global stats

sumCntFailed = 0
for key in cntfailed:
    sumCntFailed += cntfailed[key]

tempStats = [
    1, # increment for bot starting counter
    cntJoined, 
    sumCntFailed, # sum of all failed joins in the following
    cntfailed["joined_already"],
    cntfailed["game_owned"],
    cntfailed["giveaway_ended"],
    cntfailed["invalid_cookie"],
    cntfailed["group_missing"],
    cntfailed["max_entries"],
    cntfailed["not_published"],
    cntfailed["unkown"]
    ]

with open("stats.txt", "r") as file:
    inputStats = file.readlines()

i = 0 
while(i < len(inputStats)):
    inputStats[i] = inputStats[i].split(":")[0] + ":" + str(tempStats[i] + int(inputStats[i].split(":")[1])) + "\n"
    i += 1

with open("stats.txt", "w") as file:
        	file.writelines(inputStats)

logging.info("Total amount of joined giveaways in this run: >> " + str(cntJoined) + " <<")
logging.info("Bot successfully terminated.")
