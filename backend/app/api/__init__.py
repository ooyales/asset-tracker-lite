from app.api.auth import auth_bp
from app.api.assets import assets_bp
from app.api.relationships import relationships_bp
from app.api.security import security_bp
from app.api.licenses import licenses_bp
from app.api.dashboard import dashboard_bp
from app.api.wizard import wizard_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(relationships_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(licenses_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(wizard_bp)
