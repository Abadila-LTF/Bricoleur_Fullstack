from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
import bcrypt
import base64
import json
from flask import Flask
from flask import current_app

from werkzeug.exceptions import InternalServerError
from threading import Thread
import bcrypt
from flask_mail import Mail, Message
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import os.path
import datetime  
from datetime import date
from pydicom.uid import generate_uid
from flask_restful import Api , Resource , reqparse , abort , fields , marshal_with

db = SQLAlchemy()
app= Flask(__name__)


def send_async_email(app, msg):
    app.app_context().push()
    with app.app_context():
        try:
            mail = Mail(app)
            mail.send(msg)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.recipients = recipients
    msg.body = text_body
    msg.html = html_body
    app = current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()
    



class Users(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(80))
    tel = db.Column(db.Integer)
    location = db.Column(db.String(80))
    brikoleur = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime(True),default = db.func.now())
    updated_at = db.Column(db.DateTime(True),default = db.func.now() , onupdate = db.func.now())

class BricoleurData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domaine = db.Column(db.String(80))
    seniority = db.Column(db.Integer)
    wallet = db.Column(db.Integer)
    profile = db.Column(db.String(80))
    user_id = db.Column(db.Integer)


class Mission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brikoleur_id = db.Column(db.Integer)
    demandeur_id = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    accepted = db.Column(db.Boolean)


def tojson(user_id):
    user = Users.query.filter_by(public_id=user_id).first()
    if not user:
        return jsonify({'message' : 'User Not found!'})
    user_data={}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['email'] = user.email
    user_data['tel'] =user.tel
    user_data['location'] = user.location
    user_data['brikoleur'] = user.brikoleur
    user_data['admin'] = user.admin
    if user.brikoleur:
        data = BricoleurData.query.filter_by(user_id=user.id).first()
        user_data['domaine'] = data.domaine
        user_data['seniority'] = data.seniority
        user_data['wallet'] = data.wallet
        user_data['profile'] = data.profile
    return user_data


