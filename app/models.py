from . import db
from datetime import datetime


class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    project = db.Column(db.String(100))

    def __repr__(self):
        return f"<TimeEntry {self.description}>"
