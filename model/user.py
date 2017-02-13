# -*- coding: utf-8 -*-
import logging
        
class User(object):
    @classmethod
    def get_org_users(cls, db, zone, number):
        """
        获取手机号码所在的组织列表

        """
        sql = "SELECT a.org_id as id, a.user_id, b.org_name as name FROM org_user as a, organization as b WHERE mobile=%s AND status != -1"
        r = db.execute(sql, number)
        return list(r.fetchall())

    
