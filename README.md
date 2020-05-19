# Introduction
--- 
> ⚠️ **Warning**: Astats updated their robots.txt, the crawler should not be used anymore.
---

This bot crawls a third party analytics side for Steam called "AStats", collects relevant data from selected user profiles and autonomously joins active steam game key giveaways for that user. The bot simulates human behaviour, including a randomized waiting period (minimum 2 sec) after every action on the website, preventing an increased server load. 

# Install
The bot runs on Python 3.7 and needs the following modules installed: requests, requests-html, logging, termcolor, regex, urllib3

# Start and use the bot
--- 
> ⚠️ **Warning**: This crawler works, but is a simple solution, which makes **unverified HTTPS request**. Use at your own risk.
---

Before starting the bot for the first time, you have to insert the Steam community profile ID in "steam_id" and the Astats login cookie ID/PHP session ID in "accounts_cookie"/accounts_phpID for each account.

You can use the batch file(s) to start the bot using [Windows Task Scheduler](https://en.wikipedia.org/wiki/Windows_Task_Scheduler) (default: 2 accounts named main/secondary).

# Changelog
V1: basic bot (start ID arg, 2 profiles, stopping when last existing giveaway reached)

V2: advanced bot (start ID by last run, 2 profiles selected by .bat, stopping and saving status in lastID.txt, logger added)

V3: added Exception Handling (HTTP Status Code, missing internet connection), added session only counter for joined giveaways

V4: added stats.txt management

V5: finished debug-mode, added logger notification at the end, fixed bug with deleted giveaways and skipping dead IDs

V6: fixed bug with GET request failing, added exception handling, added counters/thresholds for exceptions in POST and GET

V7: fixed logging bugs, improved console display

# Preview
![Preview](https://github.com/lukasmoldon/astats-bot/blob/master/example.JPG)
