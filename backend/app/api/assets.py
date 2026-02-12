from flask import Blueprint, request, jsonify
from app.services.asset_service import AssetService
from app.errors import BadRequestError

assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')
service = AssetService()


@assets_bp.route('/', methods=['GET'])
def list_assets():
    """List all assets with optional filters.

    Query params:
        session_id: Filter by session (default: __default__)
        asset_type: Filter by asset type
        status: Filter by status
        classification / data_classification: Filter by classification
        search / q: Search query
        page: Page number (default: 1)
        per_page: Items per page (default: 50)
    """
    session_id = request.args.get('session_id', '__default__')
    asset_type = request.args.get('asset_type')
    status = request.args.get('status')
    data_classification = request.args.get('classification') or request.args.get('data_classification')
    search = request.args.get('search') or request.args.get('q')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    assets = service.find_all(
        session_id=session_id,
        asset_type=asset_type,
        status=status,
        data_classification=data_classification,
        search=search,
    )

    total = len(assets)
    start = (page - 1) * per_page
    end = start + per_page
    paged = assets[start:end]

    return jsonify({
        'assets': [a.to_dict() for a in paged],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@assets_bp.route('/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """Get a single asset by ID."""
    session_id = request.args.get('session_id', '__default__')
    asset = service.get_by_id(asset_id, session_id)
    return jsonify(asset.to_dict())


@assets_bp.route('/', methods=['POST'])
def create_asset():
    """Create a new asset."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    asset = service.create(data, changed_by=data.get('changed_by', 'api'))
    return jsonify(asset.to_dict()), 201


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """Update an existing asset."""
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    session_id = data.get('session_id', request.args.get('session_id', '__default__'))
    asset = service.update(
        asset_id, data,
        changed_by=data.get('changed_by', 'api'),
        session_id=session_id,
    )
    return jsonify(asset.to_dict())


@assets_bp.route('/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """Delete an asset."""
    session_id = request.args.get('session_id', '__default__')
    service.delete(asset_id, session_id)
    return jsonify({'message': 'Asset deleted'}), 200
