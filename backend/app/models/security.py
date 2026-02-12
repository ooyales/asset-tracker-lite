from datetime import datetime, timezone
from app.extensions import db


class SecurityBoundary(db.Model):
    __tablename__ = 'security_boundaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    boundary_type = db.Column(db.String(50))  # cui_boundary, fci_boundary, corporate
    description = db.Column(db.Text)
    cmmc_level = db.Column(db.String(20))  # level_1, level_2, level_3
    assessment_date = db.Column(db.Date)

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'boundary_type': self.boundary_type,
            'description': self.description,
            'cmmc_level': self.cmmc_level,
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
