# Introduction
--- 
> ⚠️ **Warning**: Since Astats updated their robots.txt, the crawler should not be used anymore.
---

This bot crawls a third party analytics side for Steam called [AStats](http://astats.astats.nl/astats/index.php) and autonomously joins active steam game key giveaways for selected user profiles. Users get notified about successfully won giveaways within the interface. Already joined giveaway IDs get saved separately for each account for future runs in order to prevent unnecessary double checking of giveaways. The bot simulates human behaviour, including a randomized waiting period (minimum 2 sec) after every action on the website, preventing an increased server load. 

# Install
The bot runs on Python 3.8 and needs the following modules installed: 
- [requests](https://pypi.org/project/requests/)
- [requests-html](https://pypi.org/project/requests-html/)
- [termcolor](https://pypi.org/project/termcolor/)
- [regex](https://pypi.org/project/regex/)
- [urllib3](https://pypi.org/project/urllib3/)

# Start and use the bot
--- 
> ⚠️ **Warning**: This crawler works, but represents a simple solution, which performs **unverified HTTPS requests**. Use at your own risk.
---

Before starting the bot for the first time, you have to insert personal identifiers in the [config](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py):
1. Insert your 17 digit Steam64 ID in ["*steam_id*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L5-L9) for each Steam account
2. Insert the Astats cookie ID in ["*accounts_cookie*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L11-L15) for the AStats account, which belongs to the corresponding Steam account
3. Insert the Astats PHP session ID in ["*accounts_phpID*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L17-L21)  for the AStats account, which belogns to the corresponding Steam account

You can use the batch file(s) to start the bot using [Windows Task Scheduler](https://en.wikipedia.org/wiki/Windows_Task_Scheduler) (default: 2 accounts named main/secondary).

## How to obtain the cookie and Steam64 ID
### Steam64 ID:
1. Open up your Steam client and choose `View`, then click `Settings`
2. Choose `Interface` and check the box that reads, `Display Steam URL address when available`
3. Click OK
4. Click on your Steam Profile Name on the top right corner and select `View Profile`

Your Steam64 ID will be listed in the URL at the top left (it's the 17 digit number at the end).
If you set a custom steam ID (text instead of the number), you can use a service like [Steam ID Finder](https://steamid.xyz/) to obtain your Steam64 ID from this custom ID. Use at your own risk.

### cookie ID / PHP session ID:

**Firefox:**
1. Visit [AStats](http://astats.astats.nl/astats/index.php) in your browser and login to your account.
2. Open the browser console: Press the F12 key or Ctrl + Shift + K (on Windows) / ⌘ + Option + K (on MacOS).
3. Within the console, select `Network` at the top.
4. While the console is open, visit your AStats profile page (hover over your username at the top right corner and click on `profile`).
5. Scroll to the top of the middle list and search for a row with host `astats.astats.nl` and file `User_Info.php?SteamID64=...`, click on it and select `Cookies` on the right.
6. Now you see a list containing the entry `COOKIE_NAME` needed for ["*accounts_cookie*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L11-L15) and `PHPSESSID` needed for ["*accounts_phpID*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L17-L21).

**Chrome:** 

⚠️ I highly recommend using **Firefox**, as Chrome does not provide the possibility to copy the complete `COOKIE_NAME`. ⚠️
1. Visit [AStats](http://astats.astats.nl/astats/index.php) in your browser and login to your account.
2. Open the browser console: Press the F12 key or Shift + CTRL + J (on Windows/Linux) / ⌘ + Option + J (on MacOS).
3. Within the console, select `Network` at the top.
4. While the console is open, visit your AStats profile page (hover over your username at the top right corner and click on `profile`).
5. Scroll to the top of the middle list and search for `User_Info.php?SteamID64=...`, click on it and select `Cookies` on the right.
6. Now you see a table containing the row `COOKIE_NAME` needed for ["*accounts_cookie*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L11-L15) and `PHPSESSID` needed for ["*accounts_phpID*"](https://github.com/lukasmoldon/astats-bot/blob/master/astats-bot/config.py#L17-L21).


# Changelog
- V1: basic bot (start ID arg, 2 profiles, stopping when last existing giveaway reached)
- V2: advanced bot (start ID by last run, 2 profiles selected by .bat, stopping and saving status in lastID.txt, logger added)
- V3: added Exception Handling (HTTP Status Code, missing internet connection), added session only counter for joined giveaways
- V4: added stats.txt management
- V5: finished debug-mode, added logger notification at the end, fixed bug with deleted giveaways and skipping dead IDs
- V6: fixed bug with GET request failing, added exception handling, added counters/thresholds for exceptions in POST and GET
- V7: fixed logging bugs, improved console display

# Preview
![Preview](https://github.com/lukasmoldon/astats-bot/blob/master/example.JPG)
