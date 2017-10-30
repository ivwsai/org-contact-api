from flask import request
from flask import Flask
from flask import g
import flask
import md5
import json
import os
from  libs.thumbnail import create_thumbnail
from flask import request, Blueprint
from werkzeug import secure_filename
from libs.util import make_response
from authorization import require_login
from model.user import User
import logging
import config

app = Blueprint('avatar', __name__)

def image_ext(content_type):
    if content_type == "image/png":
        return ".png"
    elif content_type == "image/jpeg":
        return ".jpg"
    else:
        return ""

@app.route("/avatars", methods=['POST'])
@require_login
def upload_avatar():
    uid = request.uid
    if 'file' not in request.files:
        return make_response(400)
    
    f = request.files['file']
    content_type = f.headers["Content-Type"] if f.headers.has_key("Content-Type") else ""
    ext = image_ext(content_type)
    if not ext:
        return make_response(400, {"error":"can't get image extenstion"})

    data = f.read()
    if not data:
        return make_response(400, {"error":"data is null"})

    name = md5.new(data).hexdigest()
    path = config.AVATAR_PATH + "/" + name + ext

    with open(path, "wb") as avatar_file:
        avatar_file.write(data)

    params = (128, 128, 1)
    th_data = create_thumbnail(data, params)
    th_name = md5.new(th_data).hexdigest()
    th_path = config.AVATAR_PATH + "/" + th_name + ".jpg"
    
    with open(th_path, "wb") as th_file:
        th_file.write(th_data)

    origin_url = request.url_root + "avatars/" + name + ext
    url = request.url_root + "avatars/" + th_name + ".jpg"
    User.set_avatar(g._db, uid, url, origin_url)
    
    obj = {"origin_url":origin_url, "url":url}
    return make_response(200, data=obj)

    
@app.route('/avatars/<image_path>', methods=['GET'])
def download_image(image_path):
    path = config.AVATAR_PATH + "/" + image_path

    with open(path, "rb") as f:
        data = f.read()
    
    if not data:
        return flask.make_response("", 404)
    else:
        res = flask.make_response(data, 200)
        if image_path.endswith(".jpg"):
            res.headers['Content-Type'] = "image/jpeg"
        elif image_path.endswith(".png"):
            res.headers['Content-Type'] = "image/png"
        else:
            print "invalid image type"
        return res


