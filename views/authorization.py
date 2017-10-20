# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from model.token import Token
from libs.util import make_response
import logging
import random
import time
import json
import base64
import md5
import requests
import config

def UNLOGIN():
    e = {"error":"未登录到组织"}
    logging.warn("未登录到组织")
    return make_response(400, e)

def INVALID_REFRESH_TOKEN():
    e = {"error":"非法的refresh token"}
    logging.warn("非法的refresh token")
    return make_response(400, e)
    
def INVALID_ACCESS_TOKEN():
    e = {"error":"非法的access token"}
    logging.warn("非法的access token")
    return make_response(400, e)

def EXPIRE_ACCESS_TOKEN():
    e = {"error":"过期的access token"}
    logging.warn("过期的access token")
    return make_response(400, e)

def require_auth(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
        else:
            return INVALID_ACCESS_TOKEN()

        number, uid, org_id, refresh_token, expires = Token.load_access_token(g.rds, tok)
        uid = int(uid) if uid else 0
        org_id = int(org_id) if org_id else 0
        expires = int(expires) if expires else 0
        if not number:
            return INVALID_ACCESS_TOKEN()
        if time.time() > expires:
            logging.debug("access token expire")
            return EXPIRE_ACCESS_TOKEN()
        
        request.uid = uid
        request.org_id = org_id
        request.number = number
        request.refresh_token = refresh_token
        request.access_token = tok
        return f(*args, **kwargs)
    return wrapper


def require_login(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Refresh-Token' in request.headers:
            tok = request.headers.get('Refresh-Token')
            number, uid, org_id = Token.load_refresh_token(g.rds, tok)
            if not number:
                return INVALID_REFRESH_TOKEN()
            if not uid or not org_id:
                return UNLOGIN()

            request.uid = uid
            request.org_id = org_id
            request.number = number
            return f(*args, **kwargs)
        elif 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
            number, uid, org_id, refresh_token, expires = Token.load_access_token(g.rds, tok)
            uid = int(uid) if uid else 0
            org_id = int(org_id) if org_id else 0
            expires = int(expires) if expires else 0
            if not number:
                return INVALID_ACCESS_TOKEN()
            if not uid:
                return UNLOGIN()
             
            if time.time() > expires:
                logging.debug("access token expire")
                return EXPIRE_ACCESS_TOKEN()
             
            request.uid = uid
            request.org_id = org_id
            request.number = number
            return f(*args, **kwargs)
        else:
            return INVALID_ACCESS_TOKEN()
        
     
    return wrapper


UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

def random_token_generator(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))
