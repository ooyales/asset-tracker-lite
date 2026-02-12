from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.extensions import db
from app.models.asset import Asset, AssetRelationship
from app.models.license import License
from app.models.change import AssetChange
from app.services.relationship_service import RelationshipService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
rel_service = RelationshipService()

TYPE_COLORS = {
    'hardware': '#337ab7',
    'software': '#5cb85c',
    'cloud_service': '#7c3aed',
    'network': '#f0ad4e',
    'contract': '#5bc0de',
}

STATUS_COLORS = {
    'active': '#5cb85c',
    'maintenance': '#f0ad4e',
    'retired': '#777',
    'disposed': '#d9534f',
    'planned': '#5bc0de',
}

CLASSIFICATION_COLORS = {
    'CUI': '#d9534f',
    'FCI': '#f0ad4e',
    'internal': '#337ab7',
    'Internal': '#337ab7',
    'Public': '#5cb85c',
    'public': '#5cb85c',
}


@dashboard_bp.route('/', methods=['GET'])
def get_dashboard():
    session_id = request.args.get('session_id', '__default__')

    # Total assets
    total_assets = Asset.query.filter_by(session_id=session_id).count()

    # Active assets
    active_assets = Asset.query.filter_by(session_id=session_id, status='active').count()

    # Counts by type -> array format for Recharts
    type_counts = db.session.query(
        Asset.asset_type, func.count(Asset.id)
    ).filter_by(session_id=session_id).group_by(Asset.asset_type).all()
    assets_by_type = [
        {'name': t.replace('_', ' ').title(), 'value': c, 'color': TYPE_COLORS.get(t, '#337ab7')}
        for t, c in type_counts
    ]

    # Counts by status -> array format
    status_counts = db.session.query(
        Asset.status, func.count(Asset.id)
    ).filter_by(session_id=session_id).group_by(Asset.status).all()
    assets_by_status = [
        {'name': s.title(), 'value': c}
        for s, c in status_counts
    ]

    # Classification breakdown -> array format
    class_counts = db.session.query(
        Asset.data_classification, func.count(Asset.id)
    ).filter_by(session_id=session_id).filter(
        Asset.data_classification.isnot(None)
    ).group_by(Asset.data_classification).all()
    classification_breakdown = [
        {'name': cls, 'value': c, 'color': CLASSIFICATION_COLORS.get(cls, '#337ab7')}
        for cls, c in class_counts
    ]

    # Expiring licenses (next 180 days) -> full License shape
    now = datetime.now(timezone.utc).date()
    cutoff = now + timedelta(days=180)
    expiring = License.query.filter(
        License.session_id == session_id,
        License.expiry_date.isnot(None),
        License.expiry_date <= cutoff,
        License.expiry_date >= now,
    ).order_by(License.expiry_date).all()

    expiring_license_list = []
    for lic in expiring:
        expiring_license_list.append({
            'id': lic.id,
            'software_name': lic.software_asset.name if lic.software_asset else 'Unknown',
            'vendor': lic.vendor or '',
            'license_type': lic.license_type or '',
            'total_seats': lic.total_seats or 0,
            'used_seats': lic.used_seats or 0,
            'annual_cost': float(lic.cost_per_period or 0) * (lic.total_seats or 0),
            'billing_period': lic.billing_period or '',
            'expiry_date': lic.expiry_date.isoformat() if lic.expiry_date else '',
            'auto_renew': lic.auto_renew or False,
            'status': 'active',
            'asset_id': lic.software_asset_id,
            'notes': lic.notes or '',
            'created_at': lic.created_at.isoformat() if lic.created_at else '',
            'updated_at': lic.updated_at.isoformat() if lic.updated_at else '',
        })

    # Recent changes (last 10) -> full AssetChange shape
    recent = AssetChange.query.filter_by(
        session_id=session_id
    ).order_by(AssetChange.changed_at.desc()).limit(10).all()

    recent_changes = [{
        'id': c.id,
        'asset_id': c.asset_id,
        'asset_name': c.asset.name if c.asset else 'Unknown',
        'change_type': c.change_type,
        'field_changed': c.field_changed or '',
        'old_value': c.old_value or '',
        'new_value': c.new_value or '',
        'changed_by': c.changed_by or '',
        'changed_at': c.changed_at.isoformat() if c.changed_at else '',
    } for c in recent]

    # Orphan count
    orphans = rel_service.get_orphans(session_id)
    orphan_count = len(orphans)

    return jsonify({
        'total_assets': total_assets,
        'active_assets': active_assets,
        'expiring_licenses': len(expiring_license_list),
        'orphan_assets': orphan_count,
        'assets_by_type': assets_by_type,
        'assets_by_status': assets_by_status,
        'classification_breakdown': classification_breakdown,
        'expiring_license_list': expiring_license_list,
        'recent_changes': recent_changes,
    })
