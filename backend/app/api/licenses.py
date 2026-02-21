from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.license import License
from app.errors import NotFoundError, BadRequestError

licenses_bp = Blueprint('licenses', __name__, url_prefix='/api/licenses')


@licenses_bp.route('/', methods=['GET'])
def list_licenses():
    """List all licenses ordered by expiry date.
    ---
    tags:
      - Licenses
    parameters:
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
        description: Filter by session
    responses:
      200:
        description: List of licenses
        schema:
          type: array
          items:
            $ref: '#/definitions/License'
    """
    session_id = request.args.get('session_id', '__default__')
    licenses = License.query.filter_by(session_id=session_id).order_by(
        License.expiry_date
    ).all()
    return jsonify([lic.to_dict() for lic in licenses])


@licenses_bp.route('/<int:license_id>', methods=['GET'])
def get_license(license_id):
    """Get a single license by ID.
    ---
    tags:
      - Licenses
    parameters:
      - name: license_id
        in: path
        type: integer
        required: true
        description: License primary key
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
    responses:
      200:
        description: License details
        schema:
          $ref: '#/definitions/License'
      404:
        description: License not found
    """
    session_id = request.args.get('session_id', '__default__')
    lic = License.query.filter_by(id=license_id, session_id=session_id).first()
    if not lic:
        raise NotFoundError(f'License {license_id} not found')
    return jsonify(lic.to_dict())


@licenses_bp.route('/', methods=['POST'])
def create_license():
    """Create a new license.
    ---
    tags:
      - Licenses
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - software_asset_id
          properties:
            software_asset_id:
              type: integer
              description: ID of the software asset this license belongs to
            license_type:
              type: string
              enum: [perpetual, subscription, per_seat, site]
            vendor:
              type: string
            total_seats:
              type: integer
            used_seats:
              type: integer
              default: 0
            cost_per_period:
              type: number
            billing_period:
              type: string
              enum: [monthly, annual]
            start_date:
              type: string
              format: date
            expiry_date:
              type: string
              format: date
            auto_renew:
              type: boolean
              default: false
            contract_number:
              type: string
            notes:
              type: string
            session_id:
              type: string
              default: __default__
    responses:
      201:
        description: License created
        schema:
          $ref: '#/definitions/License'
      400:
        description: Request body is required
    """
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
    """Update a license.
    ---
    tags:
      - Licenses
    parameters:
      - name: license_id
        in: path
        type: integer
        required: true
        description: License primary key
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            software_asset_id:
              type: integer
            license_type:
              type: string
            vendor:
              type: string
            total_seats:
              type: integer
            used_seats:
              type: integer
            cost_per_period:
              type: number
            billing_period:
              type: string
            start_date:
              type: string
              format: date
            expiry_date:
              type: string
              format: date
            auto_renew:
              type: boolean
            contract_number:
              type: string
            notes:
              type: string
            session_id:
              type: string
    responses:
      200:
        description: Updated license
        schema:
          $ref: '#/definitions/License'
      400:
        description: Request body is required
      404:
        description: License not found
    """
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
    """Delete a license.
    ---
    tags:
      - Licenses
    parameters:
      - name: license_id
        in: path
        type: integer
        required: true
        description: License primary key
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
    responses:
      200:
        description: License deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: License not found
    """
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
