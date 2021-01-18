##################################################################################################################
######################################## insert account information below ########################################
##################################################################################################################

# Steam64ID for different accounts
steam_id = {
    "main": "", # Enter Steam profile ID between the quotation marks ("here")
    "secondary": "" # Enter Steam profile ID between the quotation marks ("here")
}

# COOKIE_NAME for different accounts
accounts_cookie = {
    "main": "", # Enter Cookie ID between the quotation marks ("here")
    "secondary": "" # Enter Cookie ID between the quotation marks ("here")
}

# PHPSESSID for different accounts
accounts_phpID = {
    "main": "", # Enter PHP Session ID between the quotation marks ("here")
    "secondary": "" # Enter PHP Session ID between the quotation marks ("here")
}

##################################################################################################################
######################################## insert account information above ########################################
##################################################################################################################



# Debug Mode on?
debug = False

# After how many (successively!) requests resulting in a non existing page should the bot get terminated?
thresholdDeadPage = 3

# After how many (successively!) GET requests resulting in a HTTPS Error should the bot get terminated?
thresholdExceptionGET = 5

# After how many (successively!) POST requests resulting in a HTTPS Error should the bot get terminated?
thresholdExceptionPOST = 2