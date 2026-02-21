from flask import Blueprint, request, jsonify
from app.services.relationship_service import RelationshipService
from app.errors import BadRequestError

relationships_bp = Blueprint('relationships', __name__, url_prefix='/api/relationships')
service = RelationshipService()


@relationships_bp.route('/graph', methods=['GET'])
def get_graph():
    """Get D3-compatible graph JSON for relationship visualization.
    ---
    tags:
      - Relationships
    parameters:
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
        description: Filter by session
    responses:
      200:
        description: D3-compatible graph data
        schema:
          type: object
          properties:
            nodes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  type:
                    type: string
                  group:
                    type: string
                  color:
                    type: string
            links:
              type: array
              items:
                type: object
                properties:
                  source:
                    type: integer
                  target:
                    type: integer
                  type:
                    type: string
    """
    session_id = request.args.get('session_id', '__default__')
    graph_data = service.get_graph_json(session_id)
    return jsonify(graph_data)


@relationships_bp.route('/impact/<int:asset_id>', methods=['GET'])
def get_impact(asset_id):
    """Get downstream impact analysis for an asset using BFS traversal.
    ---
    tags:
      - Relationships
    parameters:
      - name: asset_id
        in: path
        type: integer
        required: true
        description: Asset primary key to analyze impact for
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
        description: Filter by session
      - name: depth
        in: query
        type: integer
        required: false
        default: 2
        description: Maximum BFS traversal depth (1-10)
    responses:
      200:
        description: Impact analysis result with affected assets
        schema:
          type: object
          properties:
            root_asset:
              $ref: '#/definitions/Asset'
            impacted:
              type: array
              items:
                type: object
                properties:
                  asset:
                    $ref: '#/definitions/Asset'
                  depth:
                    type: integer
                  path:
                    type: array
                    items:
                      type: string
      400:
        description: Depth must be between 1 and 10
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
    ---
    tags:
      - Relationships
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - source_asset_id
            - target_asset_id
            - relationship_type
          properties:
            source_asset_id:
              type: integer
              description: ID of the source asset
            target_asset_id:
              type: integer
              description: ID of the target asset
            relationship_type:
              type: string
              description: Type of relationship (e.g. runs, depends_on, supports, installed_on, protects)
            description:
              type: string
              description: Optional description of the relationship
            session_id:
              type: string
              default: __default__
    responses:
      201:
        description: Relationship created
        schema:
          $ref: '#/definitions/AssetRelationship'
      400:
        description: Missing required fields
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
    """Delete a relationship by ID.
    ---
    tags:
      - Relationships
    parameters:
      - name: rel_id
        in: path
        type: integer
        required: true
        description: Relationship primary key
      - name: session_id
        in: query
        type: string
        required: false
        default: __default__
    responses:
      200:
        description: Relationship deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Relationship not found
    """
    session_id = request.args.get('session_id', '__default__')
    service.delete_relationship(rel_id, session_id)
    return jsonify({'message': 'Relationship deleted'}), 200
