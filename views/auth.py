# -*- coding: utf-8 -*-
from flask import request, Blueprint, g
import random
import json
import time
import logging

from model import code
from model.token import Token
from model.user import User
from model.contact import Contact

from authorization import random_token_generator
from authorization import require_auth, require_login
from libs.util import make_response
from libs import sms
from libs import gobelieve
from libs.gconnection import GConnection
from error import *

import config

app = Blueprint('auth', __name__)


def create_verify_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def check_verify_rate(rds, zone, number):
    now = int(time.time())
    _, ts, count = code.get_verify_code(rds, zone, number)
    if count > 10 and now - ts > 30*60:
        return True
    if now - ts > 50:
        return True

    return False


def send_sms(phone_number, code, app_name):
    accountSid = config.UC_ACCOUNT_SID
    accountToken = config.UC_ACCOUNT_TOKEN
    appId = config.UC_APPID
    templateId = config.UC_TEMPLATE_ID

    param = "%s,%s"%(code, app_name)
    try:
        resp = sms.RestAPI.templateSMS(accountSid,accountToken,appId,phone_number,templateId,param)
        obj = json.loads(resp)
        if obj['resp']['respCode'] == "000000":
            logging.info("send sms success phone:%s code:%s", phone_number, code)
            return True
        else:
            logging.warning("send sms err:%s", resp)
            return False
    except Exception, e:
        logging.warning("exception:%s", str(e))
        return False

def is_test_number(number):
    if number == "13800000000" or number == "13800000001" or \
       number == "13800000002" or number == "13800000003" or \
       number == "13800000004" or number == "13800000005" or \
       number == "13800000006" or number == "13800000007" or \
       number == "13800000008" or number == "13800000009" :
        return True
    else:
        return False
    
def is_super_number(number):
    return False

@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    zone = request.args.get("zone", "")
    number = request.args.get("number", "")
    logging.info("zone:%s number:%s", zone, number)
    if not is_test_number(number) and not check_verify_rate(g.rds, zone, number):
        return OVERFLOW()
        
    vc = create_verify_code()
    code.set_verify_code(g.rds, zone, number, vc)
    data = {}
    if True:#debug
        data["code"] = vc
        data["number"] = number
        data["zone"] = zone

    if is_test_number(number):
        return make_response(200, data = data)
    if is_super_number(number):
        return make_response(200, data = data)

    if not send_sms(number, vc, config.APP_NAME):
        return SMS_FAIL()

    return make_response(200, data = data)

    
@app.route("/auth/token", methods=["POST"])
def access_token():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    c1 = obj["code"]
    number = obj["number"]
    zone = obj["zone"]
    if is_test_number(number):
        pass
    else:
        c2, timestamp, _ = code.get_verify_code(g.rds, zone, number)
        if c1 != c2:
            return INVALID_CODE()

    orgs = User.get_orgs(g._db, zone, number)
    logging.debug("orgs:%s", orgs)
    
    access_token = random_token_generator()
    refresh_token = random_token_generator()
    tok = {
        'expires_in': 3600,
        "access_token":access_token,
        "refresh_token":refresh_token,
        "organizations":orgs,
    }

    Token.save_access_token(g.rds, access_token, refresh_token, number, 3600)
    Token.save_refresh_token(g.rds, refresh_token, number)
    
    return make_response(200, tok)


@app.route("/auth/refresh_token", methods=["POST"])
def refresh_token():
    rds = g.rds
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    refresh_token = obj["refresh_token"]

    number, uid, org_id = Token.load_refresh_token(rds, refresh_token)
    if not number:
        return INVALID_REFRESH_TOKEN()

    access_token = random_token_generator()
    tok = {
        'expires_in': 3600,
        'token_type': 'Bearer',
        "access_token":access_token,
        "refresh_token":refresh_token,
        'uid':int(uid)
    }

    Token.save_access_token(g.rds, access_token, refresh_token,
                            number, 3600)
    Token.set_access_token_uid(g.rds, access_token, uid, org_id)
    
    return make_response(200, tok)

@app.route("/member/login_organization", methods=["POST"])
@require_auth
def login():
    rds = g.rds
    obj = json.loads(request.data)
    org_id = obj.get('org_id')
    if not org_id:
        return INVALID_PARAM()
    
    org_users = User.get_org_users(g._db, "86", request.number)
    logging.debug("orgs:%s %s %s", request.number, org_users, org_id)
    
    org_uid = None
    name = ""
    for u in org_users:
        if u['org_id'] == org_id:
            org_id = u['org_id']
            org_uid = u['id']
            name = u.get('name', "")
            break

    if not org_uid:
        return INVALID_PARAM()

    token = gobelieve.login_gobelieve(int(org_uid), name)
    resp = {
        "gobelieve_token":token,
        "username":name,
        "id":org_uid
    }

    access_token = request.access_token
    refresh_token = request.refresh_token
    Token.set_access_token_uid(rds, access_token, org_uid, org_id)
    Token.set_refresh_token_uid(rds, refresh_token, org_uid, org_id)
    
    return make_response(200, resp)


@app.route("/member/organizations", methods=["GET"])
@require_auth
def get_organizations():
    orgs = User.get_orgs(g._db, "86", request.number)
    return make_response(200, {"organizations":orgs})

