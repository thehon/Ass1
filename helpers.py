def PasswordRules(password):
    error = ''
    approved = True
    if (len(password) < 8):
        error = 'Password needs to be at least 8 characters'
        approved = False
        return (error, approved)
    numcaps = (sum(1 for c in password if c.isupper()))
    if (numcaps == 0):
        return ('Password needs at least 1 uppercase character', False)
    if (numcaps == len(password)):
        return ('Password needs at least 1 lowercase character', False)
    numdigits = (sum(1 for c in password if c.isdigit()))
    if (numdigits == 0):
        return ('Password needs at least 1 digit', False)
    specialChars = ['!','”','#','$', '%','&',"'",'(',')','*','+',',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', ']' '^', '_'. '`', '{', '|', '}', '~']    
    if (not any(s in specialChars for s in password)):
        return ("Password needs at least 1 special character: !”#$%&'()*+,-./:;<=>?@[\]^_`{|}~", False)

    #check if the password is in the banned list :)
    wordlist = loadwordlist()
    if (password.lower() in wordlist):
        return ("This password is banned - cant use it", False)
    
def loadwordlist():
    f = open('twitter-banned.txt', 'r')
    bannedPWs = f.read().splitlines()
    f.close()
    return bannedPWs


    