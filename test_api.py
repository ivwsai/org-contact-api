# -*- coding: utf-8 -*-

import requests
import urllib
import urllib2
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import threading
import json
import sys

URL = "http://192.168.33.10:8888"
#URL = "http://api.goubuli.mobi"
access_token = ""
refresh_tokne = ""
def LoginNumber():
    url = URL + "/verify_code?"
    NUMBER = "13800000000"
    values = {'zone' : '86', 'number' : NUMBER}
    params = urllib.urlencode(values) 
    url += params
     
    r = requests.post(url)
    print r.content
    resp = json.loads(r.content)
     
    code = resp["code"]
    url = URL + "/auth/token"
    values = {"zone":"86", "number":NUMBER, "code":code}
    data = json.dumps(values)
    r = requests.post(url, data=data)
    print r.content
    resp = json.loads(r.content)
     
    print "access token:", resp["access_token"]
    print "refresh token:", resp["refresh_token"]
    access_token = resp["access_token"]
    refresh_token = resp["refresh_token"]
    orgs = resp["organizations"]


    org_id = orgs[0]['id']
    url = URL + "/member/login_organization"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers['Content-Type'] = 'application/json'

    values = {"org_id":org_id}
    data = json.dumps(values)
    r = requests.post(url, headers=headers, data=data)
    print r.status_code, r.content
    
    
    
    url = URL + "/auth/refresh_token"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
     
    values = {"refresh_token":refresh_token}
    data = json.dumps(values)
    r = requests.post(url, data=data, headers = headers)
    print r.content
    resp = json.loads(r.content)
     
    print "access token:", resp["access_token"]
    print "refresh token:", resp["refresh_token"]
    access_token = resp["access_token"]
    refresh_token = resp["refresh_token"]

    return access_token, refresh_token    


def sync_contact():
    url = URL + "/contact/sync?sync_key=0"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    #or
    #headers['Refresh-Token'] = refresh_token
    headers['Content-Type'] = 'application/json'

    r = requests.get(url, headers=headers)
    print r.status_code, r.content    

access_token, refresh_token = LoginNumber()
sync_contact()



