from app import db
from sqlalchemy.dialects.postgresql import JSON

class Result(db.Model):
    __tablename__ = 'loadtests'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    operation_time = db.Column(db.String())
    operation_string = db.Column(db.String())
    start_date = db.Column(db.DateTime)

    def __init__(self, url, operation_time, operation_string, start_date):
        self.url = url
        self.operation_time = operation_time
        self.operation_string = operation_string
        self.start_date = start_date


    def __repr__(self):
        return '<id {}>'.format(self.id)
