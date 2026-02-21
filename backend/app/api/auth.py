from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required, get_jwt
)
from app.extensions import db
from app.models.user import User
from app.errors import BadRequestError, UnauthorizedError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token.
    ---
    tags:
      - Auth
    security: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: admin123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
              description: JWT access token
            access_token:
              type: string
              description: JWT access token (alias)
            user:
              $ref: '#/definitions/User'
      400:
        description: Missing credentials
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        raise BadRequestError('Username and password are required')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise UnauthorizedError('Invalid username or password')

    additional_claims = {
        'username': user.username,
        'role': user.role,
        'display_name': user.display_name,
    }
    access_token = create_access_token(
        identity=user.username,
        additional_claims=additional_claims,
    )

    return jsonify({
        'token': access_token,
        'access_token': access_token,
        'user': user.to_dict(),
    })


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Return current authenticated user info from JWT.
    ---
    tags:
      - Auth
    responses:
      200:
        description: Current user profile
        schema:
          type: object
          properties:
            username:
              type: string
            role:
              type: string
            display_name:
              type: string
      401:
        description: Unauthorized — missing or invalid JWT
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    return jsonify({
        'username': identity,
        'role': claims.get('role', 'viewer'),
        'display_name': claims.get('display_name', identity),
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Refresh the JWT access token.
    ---
    tags:
      - Auth
    responses:
      200:
        description: New access token
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Unauthorized — missing or invalid JWT
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    additional_claims = {
        'username': identity,
        'role': claims.get('role', 'viewer'),
        'display_name': claims.get('display_name', identity),
    }
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims,
    )
    return jsonify({'access_token': access_token})
