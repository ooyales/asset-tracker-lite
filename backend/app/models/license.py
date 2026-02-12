from datetime import datetime, timezone
from app.extensions import db


class License(db.Model):
    __tablename__ = 'licenses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    software_asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    license_type = db.Column(db.String(50))  # perpetual, subscription, per_seat, site
    vendor = db.Column(db.String(200))
    total_seats = db.Column(db.Integer)
    used_seats = db.Column(db.Integer, default=0)
    cost_per_period = db.Column(db.Float)
    billing_period = db.Column(db.String(20))  # monthly, annual
    start_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    auto_renew = db.Column(db.Boolean, default=False)
    contract_number = db.Column(db.String(100))
    notes = db.Column(db.Text)

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    software_asset = db.relationship('Asset', backref='licenses', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'software_asset_id': self.software_asset_id,
            'software_name': self.software_asset.name if self.software_asset else None,
            'license_type': self.license_type,
            'vendor': self.vendor,
            'total_seats': self.total_seats,
            'used_seats': self.used_seats,
            'cost_per_period': self.cost_per_period,
            'billing_period': self.billing_period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'auto_renew': self.auto_renew,
            'contract_number': self.contract_number,
            'notes': self.notes,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
