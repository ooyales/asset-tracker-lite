from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.security import SecurityBoundary
from app.models.asset import Asset
from app.errors import NotFoundError, BadRequestError

security_bp = Blueprint('security', __name__, url_prefix='/api/security')


@security_bp.route('/boundaries', methods=['GET'])
def list_boundaries():
    """List all security boundaries.

    Query params:
        session_id: Filter by session (default: __default__)
    """
    session_id = request.args.get('session_id', '__default__')
    boundaries = SecurityBoundary.query.filter_by(session_id=session_id).order_by(
        SecurityBoundary.name
    ).all()
    return jsonify([b.to_dict() for b in boundaries])


@security_bp.route('/boundaries/<int:boundary_id>', methods=['GET'])
def get_boundary(boundary_id):
    """Get a single security boundary by ID."""
    session_id = request.args.get('session_id', '__default__')
    boundary = SecurityBoundary.query.filter_by(
        id=boundary_id, session_id=session_id
    ).first()
    if not boundary:
        raise NotFoundError(f'Security boundary {boundary_id} not found')
    return jsonify(boundary.to_dict())


@security_bp.route('/boundaries/<int:boundary_id>/assets', methods=['GET'])
def get_boundary_assets(boundary_id):
    """Get all assets within a security boundary.

    Query params:
        session_id: Filter by session (default: __default__)
    """
    session_id = request.args.get('session_id', '__default__')
    boundary = SecurityBoundary.query.filter_by(
        id=boundary_id, session_id=session_id
    ).first()
    if not boundary:
        raise NotFoundError(f'Security boundary {boundary_id} not found')

    assets = Asset.query.filter_by(
        security_boundary_id=boundary_id, session_id=session_id
    ).order_by(Asset.name).all()

    return jsonify({
        'boundary': boundary.to_dict(),
        'assets': [a.to_dict() for a in assets],
        'count': len(assets),
    })


@security_bp.route('/boundaries', methods=['POST'])
def create_boundary():
    """Create a new security boundary."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')
    if not data.get('name'):
        raise BadRequestError('Boundary name is required')

    boundary = SecurityBoundary(
        name=data['name'],
        boundary_type=data.get('boundary_type'),
        description=data.get('description'),
        cmmc_level=data.get('cmmc_level'),
        assessment_date=_parse_date(data.get('assessment_date')),
        session_id=data.get('session_id', '__default__'),
    )
    db.session.add(boundary)
    db.session.commit()
    return jsonify(boundary.to_dict()), 201


@security_bp.route('/boundaries/<int:boundary_id>', methods=['PUT'])
def update_boundary(boundary_id):
    """Update a security boundary."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    session_id = data.get('session_id', request.args.get('session_id', '__default__'))
    boundary = SecurityBoundary.query.filter_by(
        id=boundary_id, session_id=session_id
    ).first()
    if not boundary:
        raise NotFoundError(f'Security boundary {boundary_id} not found')

    if 'name' in data:
        boundary.name = data['name']
    if 'boundary_type' in data:
        boundary.boundary_type = data['boundary_type']
    if 'description' in data:
        boundary.description = data['description']
    if 'cmmc_level' in data:
        boundary.cmmc_level = data['cmmc_level']
    if 'assessment_date' in data:
        boundary.assessment_date = _parse_date(data['assessment_date'])

    db.session.commit()
    return jsonify(boundary.to_dict())


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
