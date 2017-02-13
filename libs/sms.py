#-*- coding: utf-8 -*-

import base64
import datetime
import urllib2
import md5
import json

# 返回签名
def getSig(accountSid,accountToken,timestamp):
    sig = accountSid + accountToken + timestamp
    return md5.new(sig).hexdigest().upper()

#生成授权信息
def getAuth(accountSid,timestamp):
    src = accountSid + ":" + timestamp
    return base64.encodestring(src).strip()

#发起http请求
def urlOpen(req,data=None):
    try:
        res = urllib2.urlopen(req,data)
        data = res.read()
        res.close()
    except urllib2.HTTPError, error:
        data = error.read()
        error.close()
    return data

#生成HTTP报文
def createHttpReq(req,url,accountSid,timestamp,responseMode,body):
    req.add_header("Authorization", getAuth(accountSid,timestamp))
    if responseMode:
        req.add_header("Accept","application/"+responseMode)
        req.add_header("Content-Type","application/"+responseMode+";charset=utf-8")
    if body:
        req.add_header("Content-Length",len(body))
        req.add_data(body)
    return req

class RestAPI:
    HOST = "https://api.ucpaas.com"
    PORT = ""
    SOFTVER = "2014-06-30"
    JSON = "json"
    XML = "xml"

    #短信验证码（模板短信）
    #accountSid 主账号ID
    #accountToken 主账号Token
    #appId 应用ID
    #toNumber 被叫的号码
    #templateId 模板Id
    #param <可选> 内容数据，用于替换模板中{数字}
    @classmethod
    def templateSMS(self,accountSid,accountToken,appId,toNumbers,templateId,param):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        signature = getSig(accountSid,accountToken,timestamp)
        url = self.HOST + ":" + self.PORT + "/" + self.SOFTVER + "/Accounts/" + accountSid + "/Messages/templateSMS?sig=" + signature

        obj = {
            "appId":appId,
            "to":toNumbers,
            "templateId":templateId,
            "param":param
        }
        body = json.dumps({"templateSMS":obj})
        responseMode = self.JSON
        req = urllib2.Request(url)
        return urlOpen(createHttpReq(req,url,accountSid,timestamp,responseMode,body))
