import os
from flask import Flask
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
from flasgger import Swagger
from app.config import config
from app.extensions import db, jwt, cors
from app.errors import register_error_handlers


# SQLite doesn't auto-generate IDs for BIGINT columns, only INTEGER.
# This compile rule makes BigInteger render as INTEGER on SQLite so
# autoincrement primary keys work correctly.
@compiles(BigInteger, 'sqlite')
def _render_bigint_as_int(type_, compiler, **kw):
    return 'INTEGER'


SWAGGER_TEMPLATE = {
    "info": {
        "title": "Asset Tracker Lite API",
        "description": "API for the IT Asset Tracker — hardware/software inventory, "
                       "license management, security boundaries, relationship mapping, "
                       "and import wizard.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Enter: **Bearer {your-jwt-token}**"
        }
    },
    "security": [{"Bearer": []}],
    "basePath": "/",
    "schemes": ["http", "https"],
    "definitions": {
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "display_name": {"type": "string"},
                "email": {"type": "string"},
                "role": {"type": "string", "enum": ["admin", "viewer"]}
            }
        },
        "Asset": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "asset_type": {"type": "string", "enum": ["hardware", "software", "cloud_service", "network", "contract"]},
                "sub_type": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "retired", "in_storage", "disposed", "maintenance", "planned"]},
                "data_classification": {"type": "string", "enum": ["CUI", "FCI", "public", "internal"]},
                "classification": {"type": "string", "description": "Alias for data_classification"},
                "security_boundary_id": {"type": "integer"},
                "security_boundary_name": {"type": "string"},
                "owner_id": {"type": "integer"},
                "owner_name": {"type": "string"},
                "managed_by_id": {"type": "integer"},
                "managed_by_name": {"type": "string"},
                "vendor": {"type": "string"},
                "location_id": {"type": "integer"},
                "location_name": {"type": "string"},
                "attributes": {"type": "object", "description": "Type-specific details (JSON)"},
                "acquired_date": {"type": "string", "format": "date"},
                "warranty_expiry": {"type": "string", "format": "date"},
                "last_audit_date": {"type": "string", "format": "date"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "AssetRelationship": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "source_asset_id": {"type": "integer"},
                "source_asset_name": {"type": "string"},
                "source_asset_type": {"type": "string"},
                "target_asset_id": {"type": "integer"},
                "target_asset_name": {"type": "string"},
                "target_asset_type": {"type": "string"},
                "relationship_type": {"type": "string"},
                "description": {"type": "string"},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "License": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "software_asset_id": {"type": "integer"},
                "software_name": {"type": "string"},
                "license_type": {"type": "string", "enum": ["perpetual", "subscription", "per_seat", "site"]},
                "vendor": {"type": "string"},
                "total_seats": {"type": "integer"},
                "used_seats": {"type": "integer"},
                "cost_per_period": {"type": "number"},
                "billing_period": {"type": "string", "enum": ["monthly", "annual"]},
                "start_date": {"type": "string", "format": "date"},
                "expiry_date": {"type": "string", "format": "date"},
                "auto_renew": {"type": "boolean"},
                "contract_number": {"type": "string"},
                "notes": {"type": "string"},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "SecurityBoundary": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "boundary_type": {"type": "string", "enum": ["cui_boundary", "fci_boundary", "corporate"]},
                "description": {"type": "string"},
                "cmmc_level": {"type": "string", "enum": ["level_1", "level_2", "level_3"]},
                "assessment_date": {"type": "string", "format": "date"},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "AssetChange": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "asset_id": {"type": "integer"},
                "asset_name": {"type": "string"},
                "changed_by": {"type": "string"},
                "change_type": {"type": "string", "enum": ["created", "updated", "status_change", "relationship_added"]},
                "field_changed": {"type": "string"},
                "old_value": {"type": "string"},
                "new_value": {"type": "string"},
                "changed_at": {"type": "string", "format": "date-time"},
                "notes": {"type": "string"},
                "session_id": {"type": "string"}
            }
        },
        "Person": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "email": {"type": "string"},
                "role": {"type": "string"},
                "team": {"type": "string"},
                "phone": {"type": "string"},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        },
        "Location": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "location_type": {"type": "string", "enum": ["data_center", "office", "cloud_region", "colo"]},
                "address": {"type": "string"},
                "notes": {"type": "string"},
                "session_id": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"}
            }
        }
    }
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: rule.rule.startswith('/api/'),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Register blueprints
    from app.api import register_blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint.
        ---
        tags:
          - System
        security: []
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                timestamp:
                  type: string
                  format: date-time
                app:
                  type: string
        """
        from flask import jsonify
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'app': 'asset-tracker-lite'
        })

    # Demo auth (enabled via DEMO_AUTH_ENABLED env var)
    try:
        from demo_auth import init_demo_auth
        from demo_sessions import SessionManager
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            template_db = os.path.join(app.instance_path, db_uri.replace('sqlite:///', ''))
        else:
            template_db = os.path.join(app.instance_path, 'asset_tracker.db')
        _session_mgr = SessionManager(
            template_db=template_db,
            sessions_dir=os.path.join(os.path.dirname(app.instance_path), 'data', 'sessions')
        )
        init_demo_auth(app, session_manager=_session_mgr)
    except ImportError:
        pass

    # Register CLI commands
    register_cli(app)

    return app


def register_cli(app):
    @app.cli.command('seed')
    def seed_command():
        """Seed the database with sample data."""
        from app.seed import seed
        seed()
        print('Database seeded.')

    @app.cli.command('init-db')
    def init_db_command():
        """Create all database tables."""
        db.create_all()
        print('Database initialized.')

    @app.cli.command('reset-db')
    def reset_db_command():
        """Drop and recreate all database tables, then seed."""
        db.drop_all()
        db.create_all()
        from app.seed import seed
        seed()
        print('Database reset and seeded.')
