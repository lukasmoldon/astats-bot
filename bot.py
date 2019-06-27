import sys
import requests
import requests_html
import time
import random
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url_https = "https://astats.astats.nl/astats/Giveaway.php?GiveawayID="
acc = int(sys.argv[1])-1 # supports multiple accounts, data of that account gets selected over first argument
id = int(sys.argv[2]) # second agrument must be the AStats profile ID of that account

cookies = [
    {
    "COOKIE_NAME": "", # Enter Cookie ID here
    "cookieconsent_dismissed": "yes",
    "PHPSESSID": "" # Enter PHP Session ID here
    }, 
    {
    "COOKIE_NAME": "", # Enter Cookie ID here for another account
    "cookieconsent_dismissed": "yes",
    "PHPSESSID": "" # Enter PHP Session ID here for another account
    }
]

payload = {
    "Comment": "",
    "JoinGiveaway": "Join"
}

session_post = requests.Session()
session_get = requests_html.HTMLSession()

while(True):
    req_get = session_get.get(url_https + str(id), cookies=cookies[acc], verify=False)
    navbar = req_get.html.find(".navbar-brand")
    button = req_get.html.find("[name=JoinGiveaway]")
    if(len(navbar) > 0):
        if(len(button) > 0):
            time.sleep(5 + random.randint(1,5))
            req_post = session_post.post(url_https + str(id), cookies=cookies[acc], data=payload, verify=False)
            print("Joined giveaway [" + str(id) + "]")
        else:
            print("Giveaway [" + str(id) + "] exists, but can't be joined") #reason
    else:
        print("Reached last giveaway ID [" + str(id - 1) + "]")
        break
    id += 1
    time.sleep(7 + random.randint(1,5))
    
