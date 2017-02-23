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
        sql = "SELECT a.org_id as org_id, a.user_id as id, a.name as name, b.org_name as org_name FROM org_user as a, organization as b WHERE a.mobile=%s AND a.status != -1 AND a.org_id=b.org_id"
        r = db.execute(sql, number)
        return list(r.fetchall())    
