from flask import Flask
import logging as log
from .config import KEY_JWT,SQLALCHEMY_DATABASE_URI, MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD
from flask_jwt_extended import JWTManager
from flask_restful import Api
from .models.models import *
log.basicConfig(format='%(levelname)s:%(message)s', level=log.DEBUG)
import datetime
from flask_cors import CORS

from .resources.admin import adm
from .resources.brikoleur import bri
from .resources.demandeur import dem
from .resources.public import pub
from flask_mail import Mail ,Message

def _create_app_and_api_objects():
    # load_model()
    app = Flask(__name__)
    cors = CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800    
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 50    
    app.config['SQLALCHEMY_POOL_SIZE'] = 10    
    app.config['JWT_SECRET_KEY'] = KEY_JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'brikoleur@gmail.com',
    MAIL_PASSWORD = 'password',))
    mail = Mail(app)
    jwt = JWTManager(app)
    db.init_app(app) #db defined in api_base
    api = Api(app)
    return app, api

def create_app():
    app, api = _create_app_and_api_objects()
    app.register_blueprint(adm)
    app.register_blueprint(bri)
    app.register_blueprint(dem)
    app.register_blueprint(pub)

    return app