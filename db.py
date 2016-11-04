from flask_sqlalchemy import SQLAlchemy, sqlalchemy
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////root/lboard/map-master/database.db'
db = SQLAlchemy(app)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.String)
    amb = db.Column(db.String)

    def __init__(self, fid, amb):
        self.account_id = account_id
        self.fid = fid
        self.amb = amb

    def __repr__(self):
        return '%r' % (self.fid)
