import time
import logging

def access_token_key(token):
    return "access_token_" + token

def refresh_token_key(token):
    return "refresh_token_" + token

class Token(object):
    @classmethod
    def save_access_token(cls, rds, access_token, refresh_token, number, expires_in):
        expires = int(time.time()) + expires_in
        key = access_token_key(access_token)
        pipe = rds.pipeline()
        m = {
            "expires":expires,
            "user_id":0,
            "org_id":0,
            "number":number,
            "refresh_token":refresh_token,
        }
        pipe.hmset(key, m)
        pipe.expireat(key, expires)
        pipe.execute()

        
    @classmethod
    def set_access_token_uid(cls, rds, access_token, uid, org_id):
        key = access_token_key(access_token)        
        m = {
            "user_id":uid,
            "org_id":org_id
        }
        rds.hmset(key, m)


    @classmethod
    def load_access_token(cls, rds, access_token):
        key = access_token_key(access_token)
        return rds.hmget(key, "number", "user_id", "org_id",
                         "refresh_token", "expires")



    
    @classmethod
    def set_refresh_token_uid(cls, rds, refresh_token, uid, org_id):
        key = refresh_token_key(refresh_token)
        m = {
            "user_id":uid,
            "org_id":org_id,
        }
        rds.hmset(key, m)        
    
    @classmethod
    def save_refresh_token(cls, rds, refresh_token, number):
        key = refresh_token_key(refresh_token)
        m = {
            "user_id":0,
            "org_id":0,
            "number":number,
        }
        rds.hmset(key, m)


    @classmethod
    def load_refresh_token(cls, rds, refresh_token):
        key = refresh_token_key(refresh_token)
        return rds.hmget(key, "number", "user_id", "org_id")

