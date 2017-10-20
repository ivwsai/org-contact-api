# -*- coding: utf-8 -*-
from libs.util import make_response
import logging

def OVERFLOW():
    e = {"error":"get verify code exceed the speed rate"}
    logging.warn("get verify code exceed the speed rate")
    return make_response(400, e)

def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn("非法输入")
    return make_response(400, e)

def INVALID_CODE():
    e = {"error":"验证码错误"}
    logging.warn("验证码错误")
    return make_response(400, e)

def SMS_FAIL():
    e = {"error":"发送短信失败"}
    logging.warn("发送短信失败")
    return make_response(400, e)
    
    
def INVALID_REFRESH_TOKEN():
    e = {"error":"非法的refresh token"}
    logging.warn("非法的refresh token")
    return make_response(400, e)
 
    
def CAN_NOT_GET_TOKEN():
    e = {"error":"获取imsdk token失败"}
    logging.warn("获取imsdk token失败")
    return make_response(400, e)
   
