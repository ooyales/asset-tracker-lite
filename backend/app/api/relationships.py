from flask import Blueprint, request, jsonify
from app.services.relationship_service import RelationshipService
from app.errors import BadRequestError

relationships_bp = Blueprint('relationships', __name__, url_prefix='/api/relationships')
service = RelationshipService()


@relationships_bp.route('/graph', methods=['GET'])
def get_graph():
    """Get D3-compatible graph JSON.

    Returns {nodes: [...], links: [...]} where nodes have id, name, type, group, color
    and links have source, target, type.

    Query params:
        session_id: Filter by session (default: __default__)
    """
    session_id = request.args.get('session_id', '__default__')
    graph_data = service.get_graph_json(session_id)
    return jsonify(graph_data)


@relationships_bp.route('/impact/<int:asset_id>', methods=['GET'])
def get_impact(asset_id):
    """Get downstream impact analysis for an asset.

    Uses BFS to find all assets that depend on or are affected by the given asset.

    Query params:
        session_id: Filter by session (default: __default__)
        depth: Maximum depth for BFS traversal (default: 2)
    """
    session_id = request.args.get('session_id', '__default__')
    depth = request.args.get('depth', 2, type=int)
    if depth < 1 or depth > 10:
        raise BadRequestError('Depth must be between 1 and 10')

    result = service.get_impact(asset_id, session_id, depth)
    return jsonify(result)


@relationships_bp.route('/', methods=['POST'])
def create_relationship():
    """Create a new asset relationship.

    Request body:
        source_asset_id: ID of the source asset
        target_asset_id: ID of the target asset
        relationship_type: Type of relationship
        description: Optional description
        session_id: Optional session ID (default: __default__)
    """
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    required = ['source_asset_id', 'target_asset_id', 'relationship_type']
    missing = [f for f in required if f not in data]
    if missing:
        raise BadRequestError(f'Missing required fields: {", ".join(missing)}')

    rel = service.create_relationship(data)
    return jsonify(rel.to_dict()), 201


@relationships_bp.route('/<int:rel_id>', methods=['DELETE'])
def delete_relationship(rel_id):
    """Delete a relationship by ID."""
    session_id = request.args.get('session_id', '__default__')
    service.delete_relationship(rel_id, session_id)
    return jsonify({'message': 'Relationship deleted'}), 200
