from flask import Blueprint, request, jsonify
from app.services.wizard_service import WizardService, ENTITY_TYPES

wizard_bp = Blueprint('wizard', __name__, url_prefix='/api/wizard')
service = WizardService()


@wizard_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new wizard session."""
    result = service.create_session()
    return jsonify(result), 201


@wizard_bp.route('/entity-types', methods=['GET'])
def list_entity_types():
    """List available entity types for import."""
    return jsonify(service.get_entity_types())


@wizard_bp.route('/sample/<entity_type>', methods=['GET'])
def get_sample(entity_type):
    """Get sample CSV for an entity type."""
    sample = service.get_sample(entity_type)
    if sample is None:
        return jsonify({'error': f'Unknown entity type: {entity_type}'}), 404
    return jsonify({'entity_type': entity_type, 'csv': sample})


@wizard_bp.route('/import/<entity_type>', methods=['POST'])
def import_entity(entity_type):
    """Import data for an entity type.

    Accepts:
        - File upload (CSV or XLSX) via multipart/form-data with key 'file'
        - Pasted text (CSV) via form data with key 'text'
        - JSON body with 'text' (CSV string) or 'rows' (array of dicts)

    Headers:
        X-Session-Id: wizard session ID (or query param session_id)
    """
    if entity_type not in ENTITY_TYPES:
        return jsonify({'error': f'Unknown entity type: {entity_type}'}), 404

    session_id = request.headers.get('X-Session-Id') or request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required (header X-Session-Id or query param)'}), 400

    # Check if this is a file upload or JSON body
    if request.files and 'file' in request.files:
        file = request.files['file']
        rows = service.parse_file(file)
    elif request.content_type and 'multipart' in request.content_type:
        # Pasted text sent as form data
        text = request.form.get('text', '')
        rows = service.parse_csv_text(text)
    else:
        data = request.get_json(silent=True) or {}
        if 'text' in data:
            rows = service.parse_csv_text(data['text'])
        elif 'rows' in data:
            rows = data['rows']
        else:
            return jsonify({'error': 'Provide file upload, text (CSV), or rows (JSON array)'}), 400

    result = service.import_entity(session_id, entity_type, rows)
    status = 200 if not result['errors'] else 207  # 207 Multi-Status if partial
    return jsonify(result), status


@wizard_bp.route('/preview/<entity_type>', methods=['GET'])
def get_preview(entity_type):
    """Preview imported data for an entity type."""
    session_id = request.headers.get('X-Session-Id') or request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    rows = service.get_preview(session_id, entity_type)
    return jsonify({'entity_type': entity_type, 'rows': rows, 'count': len(rows)})


@wizard_bp.route('/status', methods=['GET'])
def get_status():
    """Get import status for a wizard session."""
    session_id = request.headers.get('X-Session-Id') or request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    status = service.get_session_status(session_id)
    if status is None:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(status)


@wizard_bp.route('/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear all data for a wizard session."""
    service.clear_session(session_id)
    return jsonify({'message': 'Session cleared'}), 200
