import requests
def getwafconfig():
    f = open('config.txt', 'r')
    configlines = f.read().splitlines()
    configpath = configlines[0]
    f.close()
    return configpath

def cleanStrings(type, path, data,user=''):
    pathdic = {}
    pathdic['login'] = '/waf/login'
    pathdic['register'] = '/waf/register'
    pathdic['search'] = '/waf/search/'+ path + '/' + user
    pathdic['commment'] = '/waf/' + path + '/' + user
    pathdic['addcourse'] = '/waf/addcourse/' + user
    pathdic['message'] = '/waf/message/' + user
    data['user'] = user
    fullwafpath = getwafconfig + pathdic[path]
    resp = request.post(fullwafpath, data)    
    resp = resp.json()    
    return resp

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
