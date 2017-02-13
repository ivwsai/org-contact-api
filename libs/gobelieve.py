# -*- coding: utf-8 -*-
import logging
import random
import time
import web
import json
import base64
import md5
import requests
import config


def login_gobelieve(uid, uname):
    appid = config.APP_ID
    appsecret = config.APP_SECRET
    
    url = config.GOBELIEVE_URL + "/auth/grant"
    obj = {"uid":uid, "user_name":uname}

    m = md5.new(appsecret)
    secret = m.hexdigest()
    basic = base64.b64encode(str(appid) + ":" + secret)

    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
     
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    if res.status_code != 200:
        logging.warning("login error:%s %s", res.status_code, res.text)
        return None

    obj = json.loads(res.text)
    return obj["data"]["token"]



def send_system_message(uid, content):
    appid = config.APP_ID
    appsecret = config.APP_SECRET
    
    url = config.GOBELIEVE_URL + "/messages/systems"
    obj = {
        "receiver":uid,
        "content":content
    }
    
    secret = md5.new(appsecret).digest().encode("hex")
    basic = base64.b64encode(str(appid) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
     
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    return res.status_code == 200
    
