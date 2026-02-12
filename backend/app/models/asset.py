from datetime import datetime, timezone
from app.extensions import db


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_type = db.Column(db.String(50), nullable=False)  # hardware, software, cloud_service, license, network, contract
    sub_type = db.Column(db.String(50))  # server, workstation, laptop, switch, firewall, SaaS, IaaS, etc.
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(30), default='active')  # active, retired, in_storage, disposed, maintenance
    data_classification = db.Column(db.String(30))  # CUI, FCI, public, internal

    security_boundary_id = db.Column(db.Integer, db.ForeignKey('security_boundaries.id'))
    owner_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    managed_by_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    vendor = db.Column(db.String(200))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    attributes = db.Column(db.JSON)  # type-specific details
    acquired_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    last_audit_date = db.Column(db.Date)
    tags = db.Column(db.JSON)  # array of strings

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    security_boundary = db.relationship('SecurityBoundary', backref='assets', lazy='joined')
    owner = db.relationship('Person', foreign_keys=[owner_id], backref='owned_assets', lazy='joined')
    managed_by = db.relationship('Person', foreign_keys=[managed_by_id], backref='managed_assets', lazy='joined')
    location = db.relationship('Location', backref='assets', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'asset_type': self.asset_type,
            'sub_type': self.sub_type,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'data_classification': self.data_classification,
            'classification': self.data_classification,
            'security_boundary_id': self.security_boundary_id,
            'security_boundary_name': self.security_boundary.name if self.security_boundary else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else None,
            'managed_by_id': self.managed_by_id,
            'managed_by_name': self.managed_by.name if self.managed_by else None,
            'vendor': self.vendor,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else None,
            'attributes': self.attributes or {},
            'acquired_date': self.acquired_date.isoformat() if self.acquired_date else None,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'last_audit_date': self.last_audit_date.isoformat() if self.last_audit_date else None,
            'tags': self.tags or [],
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AssetRelationship(db.Model):
    __tablename__ = 'asset_relationships'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    target_asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    relationship_type = db.Column(db.String(50), nullable=False)
    # runs, depends_on, supports, assigned_to, licensed_under, located_at,
    # documented_in, within_boundary, managed_by, installed_on, protects
    description = db.Column(db.Text)

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    source_asset = db.relationship('Asset', foreign_keys=[source_asset_id],
                                   backref='outgoing_relationships', lazy='joined')
    target_asset = db.relationship('Asset', foreign_keys=[target_asset_id],
                                   backref='incoming_relationships', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'source_asset_id': self.source_asset_id,
            'source_asset_name': self.source_asset.name if self.source_asset else None,
            'source_asset_type': self.source_asset.asset_type if self.source_asset else None,
            'target_asset_id': self.target_asset_id,
            'target_asset_name': self.target_asset.name if self.target_asset else None,
            'target_asset_type': self.target_asset.asset_type if self.target_asset else None,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
