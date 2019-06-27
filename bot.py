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
# Get account name from first console argument
account_name = sys.argv[1] # supports multiple accounts, data of that account gets selected over first argument (name of account: main/secondary)


# Read last IDs
with open("lastIDs.txt", "r") as file:
    input = file.readlines()

id = 99999

i = 0 
while(i < len(input)):
    input[i] = input[i].rstrip()
    str_split = input[i].split(":")
    if (str_split[0] == account_name):
        id = int(str_split[1])
    i += 1

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

# Payload for joining the giveaway
payload_ga = {
    "Comment": "",
    "JoinGiveaway": "Join"
}

#Sessions for GET and POST requests
session_ga_post = requests.Session()
session_ga_get = requests_html.HTMLSession()

while(True):
	# GET request for giveaway page
    req_ga_get = session_ga_get.get(url_ga + str(id), cookies=cookies_ga, verify=False)
    # Search for the navbar -> Page exists
    navbar = req_ga_get.html.find(".navbar-brand")
    # Search for button to join the giveaway
    button = req_ga_get.html.find("[name=JoinGiveaway]")
    if(len(navbar) > 0):
        if(len(button) > 0):
            time.sleep(1 + random.randint(1, 5))
            # POST request to join the giveaway
            req_ga_post = session_ga_post.post(url_ga + str(id), cookies=cookies_ga, data=payload_ga, verify=False)
            logging.info("Joined giveaway [" + str(id) + "]")
        else:
            # join button not found
            content_ga = req_ga_get.text
            message_ga = "Giveaway [" + str(id) + "] exists, but can't be joined. Reason: "
            if(content_ga.find("You have joined this giveaway already.") > -1):
                logging.info(message_ga + "Giveaway already joined.")
            elif(content_ga.find("You already own the giveaway game.") > -1):
                logging.info(message_ga + "Giveaway game already in steam library")
            elif(content_ga.find("This giveaway has ended.") > -1):
                logging.info(message_ga + "Giveaway ended.")
            elif(content_ga.find("You need to be logged in to participate in giveaways.") > -1):
                logging.critical(message_ga + "Cookie invalid!")
                break
            elif(content_ga.find("not in the required group") > -1):
                logging.warning(message_ga + "Group membership missing for " + re.search('Steam group member of (.*)</td>', content_ga).group(1))
            elif(content_ga.find("aximum entries") > -1):
                logging.info(message_ga + "Maximum entries reached.")
            elif(content_ga.find("This giveaway has not been published.") > -1):
                logging.info(message_ga + "Giveaway has not been published yet.")
            else:
                logging.critical(message_ga + "Unknown reason!")
    else:
        logging.info("Reached last giveaway ID [" + str(id - 1) + "]")
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
    time.sleep(1 + random.randint(1, 5))