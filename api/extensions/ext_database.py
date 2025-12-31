import logging

from flask import Flask

from models.engine import db

logger = logging.getLogger(__name__)

def init_app(app: Flask):
    
    db.init_app(app)