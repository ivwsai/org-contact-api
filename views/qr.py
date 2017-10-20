# -*- coding: utf-8 -*-
from flask import request, Blueprint, g
import random
import json
import time
import logging
import base64
import uuid
import qrcode
import StringIO
import redis

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

app = Blueprint('qr', __name__)


def wait_sweep(sid):
    key = "session_queue_" + sid
    rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                            password=config.REDIS_PASSWORD, db=config.REDIS_DB)
    rds.connection_pool.connection_class = GConnection
    e = rds.brpop(key, timeout=55)
    return e


def post_sweep_notification(rds, sid):
    key = "session_queue_" + sid
    pipe = rds.pipeline()
    pipe.rpush(key, "e")
    pipe.expire(key, 30*60)
    pipe.execute()
    

class Session:
    def __init__(self):
        self.sid = None
        self.uid = None
        self.org_id = None
        self.is_valid = False

    def save(self, rds):
        key = "session_" + self.sid
        obj = {
            "uid":self.uid,
            "org_id":self.org_id
        }
        pipe = rds.pipeline()
        pipe.hmset(key, obj)
        pipe.expire(key, 30*60)
        pipe.execute()

    def load(self, rds):
        key = "session_" + self.sid
        self.is_valid = rds.exists(key)        
        self.uid, self.org_id = rds.hmget(key, "uid", "org_id")

            
@app.route("/qrcode/session")
def get_session():
    rds = g.rds
    sid = str(uuid.uuid1())
    session = Session()
    session.sid = sid
    session.uid = ""
    session.save(rds)
    logging.debug("new sid:%s", sid)
    return json.dumps({"sid":sid})    


@app.route("/qrcode/scan", methods=["POST"])
@require_login
def scan_qrcode():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)    
    sid = obj.get("sid")
    if not sid:
        return INVALID_PARAM()

    rds = g.rds
    session = Session()
    session.sid = sid
    session.uid = request.uid
    session.org_id = request.org_id
    session.save(rds)
    post_sweep_notification(rds, sid)
    return make_response(200, {"success": True})



def login_session(session, rds, db):
    u = User.get_org_user(db, session.uid)
    token = gobelieve.login_gobelieve(int(session.uid), u['name'])
    if not token:
        return make_response(400, {"error":"can't get im token"})
                             
    name = u['name']
    org_name = u['org_name']
    number = u['mobile']
    org_uid = session.uid
    org_id = session.org_id

    access_token = random_token_generator()
    refresh_token = random_token_generator()
    Token.save_access_token(g.rds, access_token, refresh_token, number, 3600)
    Token.save_refresh_token(g.rds, refresh_token, number)

    Token.set_access_token_uid(rds, access_token, org_uid, org_id)
    Token.set_refresh_token_uid(rds, refresh_token, org_uid, org_id)

    resp = {
        "gobelieve_token":token,
        "username":name,
        "uid":session.uid,
        "org_id":session.org_id,
        "org_name":org_name,
        "access_token":access_token,
        "refresh_token":refresh_token,
        "expires_in":3600
    }    
    return make_response(200, resp)

  
@app.route("/qrcode/login")
def login():
    logging.debug("qrcode login")
    sid = request.args.get('sid')
    if not sid:
        return INVALID_PARAM()
    
    rds = g.rds
    session = Session()
    session.sid = sid
    session.load(rds)
     
    if not session.is_valid:
        logging.debug("sid not found")
        return make_response(404, {"error":"sid not found"})
     
    if session.uid:
        #已经登录
        return login_session(session, rds, g._db)
     
    e = wait_sweep(sid)
    if not e:
        logging.debug("qrcode login timeout")
        return make_response(400, {"error":"timeout"})                

    session.load(rds)
    if not session.is_valid:
        return make_response(400, {"error":"timeout"})        
     
    if session.uid:
        #登录成功
        return login_session(session, rds, g._db)

    logging.warning("session login fail")
    return make_response(400, {"error":"timeout"})


@app.route("/qrcode/<id>")
def get_qrcode_image(id):
    logging.debug("qrcode id:%s", id)
    img = qrcode.make(id)
    output = StringIO.StringIO()
    img.save(output)
    return output.getvalue()    
