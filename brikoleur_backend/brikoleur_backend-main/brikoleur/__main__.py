#!/bin/env python 
# from .main import db
from .config import SERVER_HOST
from . import create_app
from .models.models import *
def init_db():
    db.create_all()

def run_app():
    app = create_app()
    with app.app_context():
        init_db()
    app.run(debug=True, host=SERVER_HOST)

run_app()