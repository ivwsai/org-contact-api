# -*- coding: utf-8 -*-
class Contact(object):
    @classmethod
    def get_contacts(cls, db, org_id, ts):
        """
        获取时间戳之后的联系人
        """
        sql = "SELECT user_id, dept_id, name, avatar, origin_avatar, mobile, email, status, update_time FROM org_user WHERE update_time >= %s AND org_id=%s ORDER BY update_time"
        r = db.execute(sql, (ts, org_id))
        return list(r.fetchall())


    @classmethod
    def get_departments(cls, db, org_id, ts):
        """
        获取时间戳之后的部门
        """
        sql = "SELECT dept_id, name, status, parent_id, update_time FROM org_dept WHERE update_time >= %s AND org_id=%s ORDER BY update_time"
        r = db.execute(sql, (ts, org_id))
        return list(r.fetchall())
