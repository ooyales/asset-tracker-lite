from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.license import License
from app.errors import NotFoundError, BadRequestError

licenses_bp = Blueprint('licenses', __name__, url_prefix='/api/licenses')


@licenses_bp.route('/', methods=['GET'])
def list_licenses():
    """List all licenses.

    Query params:
        session_id: Filter by session (default: __default__)
    """
    session_id = request.args.get('session_id', '__default__')
    licenses = License.query.filter_by(session_id=session_id).order_by(
        License.expiry_date
    ).all()
    return jsonify([lic.to_dict() for lic in licenses])


@licenses_bp.route('/<int:license_id>', methods=['GET'])
def get_license(license_id):
    """Get a single license by ID."""
    session_id = request.args.get('session_id', '__default__')
    lic = License.query.filter_by(id=license_id, session_id=session_id).first()
    if not lic:
        raise NotFoundError(f'License {license_id} not found')
    return jsonify(lic.to_dict())


@licenses_bp.route('/', methods=['POST'])
def create_license():
    """Create a new license."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    lic = License(
        software_asset_id=data.get('software_asset_id'),
        license_type=data.get('license_type'),
        vendor=data.get('vendor'),
        total_seats=data.get('total_seats'),
        used_seats=data.get('used_seats', 0),
        cost_per_period=data.get('cost_per_period'),
        billing_period=data.get('billing_period'),
        start_date=_parse_date(data.get('start_date')),
        expiry_date=_parse_date(data.get('expiry_date')),
        auto_renew=data.get('auto_renew', False),
        contract_number=data.get('contract_number'),
        notes=data.get('notes'),
        session_id=data.get('session_id', '__default__'),
    )
    db.session.add(lic)
    db.session.commit()
    return jsonify(lic.to_dict()), 201


@licenses_bp.route('/<int:license_id>', methods=['PUT'])
def update_license(license_id):
    """Update a license."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    session_id = data.get('session_id', request.args.get('session_id', '__default__'))
    lic = License.query.filter_by(id=license_id, session_id=session_id).first()
    if not lic:
        raise NotFoundError(f'License {license_id} not found')

    updatable = [
        'software_asset_id', 'license_type', 'vendor', 'total_seats',
        'used_seats', 'cost_per_period', 'billing_period', 'auto_renew',
        'contract_number', 'notes',
    ]
    for field in updatable:
        if field in data:
            setattr(lic, field, data[field])

    date_fields = ['start_date', 'expiry_date']
    for field in date_fields:
        if field in data:
            setattr(lic, field, _parse_date(data[field]))

    db.session.commit()
    return jsonify(lic.to_dict())


@licenses_bp.route('/<int:license_id>', methods=['DELETE'])
def delete_license(license_id):
    """Delete a license."""
    session_id = request.args.get('session_id', '__default__')
    lic = License.query.filter_by(id=license_id, session_id=session_id).first()
    if not lic:
        raise NotFoundError(f'License {license_id} not found')
    db.session.delete(lic)
    db.session.commit()
    return jsonify({'message': 'License deleted'}), 200


def _parse_date(value):
    """Parse a date string (YYYY-MM-DD) or return None."""
    if not value:
        return None
    if isinstance(value, str):
        from datetime import datetime
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None
    return value
