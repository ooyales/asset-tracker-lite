from flask import Blueprint, request, jsonify
from app.services.asset_service import AssetService
from app.errors import BadRequestError

assets_bp = Blueprint('assets', __name__, url_prefix='/api/assets')
service = AssetService()


@assets_bp.route('/', methods=['GET'])
def list_assets():
    """List all assets with optional filters and pagination.
    ---
    tags:
      - Assets
    parameters:
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
        description: Filter by session
      - name: asset_type
        in: query
        type: string
        required: false
        enum: [hardware, software, cloud_service, network, contract]
        description: Filter by asset type
      - name: status
        in: query
        type: string
        required: false
        enum: [active, retired, in_storage, disposed, maintenance, planned]
        description: Filter by status
      - name: classification
        in: query
        type: string
        required: false
        enum: [CUI, FCI, public, internal]
        description: Filter by data classification (alias data_classification)
      - name: search
        in: query
        type: string
        required: false
        description: Search across name, description, vendor (alias q)
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        default: 50
        description: Items per page
    responses:
      200:
        description: Paginated list of assets
        schema:
          type: object
          properties:
            assets:
              type: array
              items:
                $ref: '#/definitions/Asset'
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
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
    """Get a single asset by ID.
    ---
    tags:
      - Assets
    parameters:
      - name: asset_id
        in: path
        type: integer
        required: true
        description: Asset primary key
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
    responses:
      200:
        description: Asset details
        schema:
          $ref: '#/definitions/Asset'
      404:
        description: Asset not found
    """
    session_id = request.args.get('session_id', '__default__')
    asset = service.get_by_id(asset_id, session_id)
    return jsonify(asset.to_dict())


@assets_bp.route('/', methods=['POST'])
def create_asset():
    """Create a new asset.
    ---
    tags:
      - Assets
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - asset_type
          properties:
            name:
              type: string
            asset_type:
              type: string
              enum: [hardware, software, cloud_service, network, contract]
            sub_type:
              type: string
            description:
              type: string
            status:
              type: string
              default: active
            data_classification:
              type: string
              enum: [CUI, FCI, public, internal]
            security_boundary_id:
              type: integer
            owner_id:
              type: integer
            managed_by_id:
              type: integer
            vendor:
              type: string
            location_id:
              type: integer
            attributes:
              type: object
            acquired_date:
              type: string
              format: date
            warranty_expiry:
              type: string
              format: date
            last_audit_date:
              type: string
              format: date
            tags:
              type: array
              items:
                type: string
            session_id:
              type: string
              default: __default__
            changed_by:
              type: string
              description: Username for change audit trail
    responses:
      201:
        description: Asset created
        schema:
          $ref: '#/definitions/Asset'
      400:
        description: Request body is required
    """
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    asset = service.create(data, changed_by=data.get('changed_by', 'api'))
    return jsonify(asset.to_dict()), 201


@assets_bp.route('/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """Update an existing asset.
    ---
    tags:
      - Assets
    parameters:
      - name: asset_id
        in: path
        type: integer
        required: true
        description: Asset primary key
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            asset_type:
              type: string
            sub_type:
              type: string
            description:
              type: string
            status:
              type: string
            data_classification:
              type: string
            security_boundary_id:
              type: integer
            owner_id:
              type: integer
            managed_by_id:
              type: integer
            vendor:
              type: string
            location_id:
              type: integer
            attributes:
              type: object
            acquired_date:
              type: string
              format: date
            warranty_expiry:
              type: string
              format: date
            last_audit_date:
              type: string
              format: date
            tags:
              type: array
              items:
                type: string
            session_id:
              type: string
            changed_by:
              type: string
              description: Username for change audit trail
    responses:
      200:
        description: Updated asset
        schema:
          $ref: '#/definitions/Asset'
      400:
        description: Request body is required
      404:
        description: Asset not found
    """
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
    """Delete an asset.
    ---
    tags:
      - Assets
    parameters:
      - name: asset_id
        in: path
        type: integer
        required: true
        description: Asset primary key
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
    responses:
      200:
        description: Asset deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Asset not found
    """
    session_id = request.args.get('session_id', '__default__')
    service.delete(asset_id, session_id)
    return jsonify({'message': 'Asset deleted'}), 200
