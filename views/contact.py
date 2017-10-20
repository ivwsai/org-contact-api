# -*- coding: utf-8 -*-
from flask import request, Blueprint, g
import random
import json
import time
import logging

from model.contact import Contact
from authorization import require_auth, require_login
from libs.util import make_response

app = Blueprint('contact', __name__)

@app.route("/contact/sync", methods=["GET"])
@require_login
def sync_contact():
    sync_key = request.args.get("sync_key", 0)
    sync_key = int(sync_key)
    org_id = request.org_id

    contacts = Contact.get_contacts(g._db, org_id, sync_key)
    depts = Contact.get_departments(g._db, org_id, sync_key)

    logging.debug("contacts:%s", contacts)
    logging.debug("departments:%s", depts)
    logging.debug("sync key:%s", sync_key)
    
    #如果多个联系人的时间戳和$ts相等，那么就返回和$ts相等的联系人
    #否则只返回大于$ts的联系人
    count = len([c for c in contacts if c['update_time'] == sync_key])
    if count <= 1:
        contacts = [c for c in contacts if c['update_time'] > sync_key]

    count = len([c for c in depts if c['update_time'] == sync_key])
    if count <= 1:
        depts = [c for c in depts if c['update_time'] > sync_key]

    logging.debug("contacts:%s", contacts)
    logging.debug("departments:%s", depts)

    #找到最大的时间戳
    for i, contact in enumerate(contacts):
        if contact['update_time'] > sync_key:
            sync_key = contact['update_time']
        
        #deleted
        if contact['status'] == -1:
            contacts[i] = {
                "user_id":contact['user_id'],
                "deleted":1
            }
            
    for i, dept in enumerate(depts):
        if dept['update_time'] > sync_key:
            sync_key = dept['update_time']

        #deleted
        if dept['status'] == -1:
            depts[i] = {
                "dept_id":dept['dept_id'],
                "deleted":1
            }
    
    resp = {
        "sync_key":sync_key,
        "contacts":contacts,
        "departments":depts
    }
    return make_response(200, resp)
