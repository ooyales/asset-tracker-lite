from datetime import datetime, timezone
from app.extensions import db


class Person(db.Model):
    __tablename__ = 'people'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    role = db.Column(db.String(100))
    team = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'team': self.team,
            'phone': self.phone,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
