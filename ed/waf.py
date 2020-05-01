import requests
def getwafconfig():
    f = open('config.txt', 'r')
    configlines = f.read().splitlines()
    configpath = configlines[0]
    f.close()
    return configpath

def cleanStrings(posttype, path, data,user=''):
    try:
        pathdic = {}
        pathdic['login'] = '/waf/login'
        pathdic['register'] = '/waf/register'
        pathdic['search'] = '/waf/search'+ path + '/' + user
        pathdic['comment'] = '/waf/comment' + path + '/' + user
        pathdic['addcourse'] = '/waf/addcourse/' + user
        pathdic['message'] = '/waf/message/' + user
        pathdic['changeprofile'] = '/waf/changeprofile/' + user 
        data['user'] = user
        fullwafpath = getwafconfig() + pathdic[posttype]

        resp = requests.post(fullwafpath, data)    
        print('response: ', resp)
        resp = resp.json()    
        print('repsonse json', resp)
    except Exception as e:
        print('error @ clean Strings: ', e)
        return data
    
    return resp

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_waf_entries():
    try:
        wafentries = requests.get(getwafconfig() + '/waf/getEntries')
        wafentries = wafentries.json()
        return wafentries
    except:
        return {}
