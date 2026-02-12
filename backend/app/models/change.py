from datetime import datetime, timezone
from app.extensions import db


class AssetChange(db.Model):
    __tablename__ = 'asset_changes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    changed_by = db.Column(db.String(200))
    change_type = db.Column(db.String(50), nullable=False)
    # created, updated, status_change, relationship_added
    field_changed = db.Column(db.String(100))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text)

    session_id = db.Column(db.String(64), nullable=False, default='__default__', index=True)

    # Relationships
    asset = db.relationship('Asset', backref='changes', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'asset_name': self.asset.name if self.asset else None,
            'changed_by': self.changed_by,
            'change_type': self.change_type,
            'field_changed': self.field_changed,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'notes': self.notes,
            'session_id': self.session_id,
        }
