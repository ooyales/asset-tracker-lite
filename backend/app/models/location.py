from datetime import datetime, timezone
from app.extensions import db


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(50))  # data_center, office, cloud_region, colo
    address = db.Column(db.Text)
    notes = db.Column(db.Text)

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location_type': self.location_type,
            'address': self.address,
            'notes': self.notes,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
