# -*- coding: utf-8 -*-
import logging
        
class User(object):
    @classmethod
    def get_orgs(cls, db, zone, number):
        """
        获取手机号码所在的组织列表

        """
        sql = "SELECT a.org_id as id, a.user_id, b.org_name as name FROM org_user as a, organization as b WHERE a.mobile=%s AND a.status != -1 AND a.org_id=b.org_id"
        r = db.execute(sql, number)
        return list(r.fetchall())

    @classmethod
    def get_org_users(cls, db, zone, number):
        """
        获取手机号码所在的组织列表

        """
        sql = "SELECT a.org_id as org_id, a.user_id as id, a.name as name, a.avatar as avatar, a.origin_avatar as origin_avatar, b.org_name as org_name FROM org_user as a, organization as b WHERE a.mobile=%s AND a.status != -1 AND a.org_id=b.org_id"
        r = db.execute(sql, number)
        return list(r.fetchall())    

    @classmethod
    def get_org_user(cls, db, uid):
        sql = "SELECT user_id as id, name, mobile, org_name FROM org_user, organization WHERE user_id=%s AND org_user.org_id=organization.org_id"
        r = db.execute(sql, uid)
        return r.fetchone()

    @classmethod
    def set_avatar(cls, db, uid, url, origin_url):
        sql = "UPDATE org_user SET avatar=%s, origin_avatar=%s WHERE user_id=%s"
        r = db.execute(sql, (url, origin_url, uid))
        return r.rowcount        
