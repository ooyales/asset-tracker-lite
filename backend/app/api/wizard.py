from flask import Blueprint, request, jsonify
from app.services.wizard_service import WizardService, ENTITY_TYPES

wizard_bp = Blueprint('wizard', __name__, url_prefix='/api/wizard')
service = WizardService()


@wizard_bp.route('/session', methods=['POST'])
def create_session():
    """Create a new wizard import session.
    ---
    tags:
      - Wizard
    responses:
      201:
        description: Wizard session created
        schema:
          type: object
          properties:
            session_id:
              type: string
            created_at:
              type: string
              format: date-time
    """
    result = service.create_session()
    return jsonify(result), 201


@wizard_bp.route('/entity-types', methods=['GET'])
def list_entity_types():
    """List available entity types for import.
    ---
    tags:
      - Wizard
    responses:
      200:
        description: Available entity types
        schema:
          type: array
          items:
            type: object
            properties:
              key:
                type: string
              label:
                type: string
              description:
                type: string
    """
    return jsonify(service.get_entity_types())


@wizard_bp.route('/sample/<entity_type>', methods=['GET'])
def get_sample(entity_type):
    """Get sample CSV template for an entity type.
    ---
    tags:
      - Wizard
    parameters:
      - name: entity_type
        in: path
        type: string
        required: true
        description: Entity type (e.g. assets, people, locations, licenses, relationships, boundaries)
    responses:
      200:
        description: Sample CSV content
        schema:
          type: object
          properties:
            entity_type:
              type: string
            csv:
              type: string
              description: CSV template text with headers and example rows
      404:
        description: Unknown entity type
    """
    sample = service.get_sample(entity_type)
    if sample is None:
        return jsonify({'error': f'Unknown entity type: {entity_type}'}), 404
    return jsonify({'entity_type': entity_type, 'csv': sample})


@wizard_bp.route('/import/<entity_type>', methods=['POST'])
def import_entity(entity_type):
    """Import data for an entity type from CSV/XLSX file, pasted CSV text, or JSON rows.
    ---
    tags:
      - Wizard
    consumes:
      - multipart/form-data
      - application/json
    parameters:
      - name: entity_type
        in: path
        type: string
        required: true
        description: Entity type (e.g. assets, people, locations, licenses, relationships, boundaries)
      - name: X-Session-Id
        in: header
        type: string
        required: false
        description: Wizard session ID (alternative to session_id query param)
      - name: session_id
        in: query
        type: string
        required: false
        description: Wizard session ID (alternative to X-Session-Id header)
      - name: file
        in: formData
        type: file
        required: false
        description: CSV or XLSX file upload
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            text:
              type: string
              description: Pasted CSV text
            rows:
              type: array
              description: Array of row objects
              items:
                type: object
    responses:
      200:
        description: Import successful (all rows imported)
        schema:
          type: object
          properties:
            imported:
              type: integer
            errors:
              type: array
              items:
                type: string
      207:
        description: Partial import (some rows had errors)
      400:
        description: Missing session_id or no data provided
      404:
        description: Unknown entity type
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
    """Preview imported data for an entity type.
    ---
    tags:
      - Wizard
    parameters:
      - name: entity_type
        in: path
        type: string
        required: true
        description: Entity type to preview
      - name: X-Session-Id
        in: header
        type: string
        required: false
        description: Wizard session ID (alternative to session_id query param)
      - name: session_id
        in: query
        type: string
        required: false
        description: Wizard session ID (alternative to X-Session-Id header)
    responses:
      200:
        description: Preview of imported rows
        schema:
          type: object
          properties:
            entity_type:
              type: string
            rows:
              type: array
              items:
                type: object
            count:
              type: integer
      400:
        description: session_id is required
    """
    session_id = request.headers.get('X-Session-Id') or request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    rows = service.get_preview(session_id, entity_type)
    return jsonify({'entity_type': entity_type, 'rows': rows, 'count': len(rows)})


@wizard_bp.route('/status', methods=['GET'])
def get_status():
    """Get import status for a wizard session.
    ---
    tags:
      - Wizard
    parameters:
      - name: X-Session-Id
        in: header
        type: string
        required: false
        description: Wizard session ID (alternative to session_id query param)
      - name: session_id
        in: query
        type: string
        required: false
        description: Wizard session ID (alternative to X-Session-Id header)
    responses:
      200:
        description: Session import status
        schema:
          type: object
          properties:
            session_id:
              type: string
            entity_counts:
              type: object
              description: Count of imported rows per entity type
            created_at:
              type: string
              format: date-time
      400:
        description: session_id is required
      404:
        description: Session not found
    """
    session_id = request.headers.get('X-Session-Id') or request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400

    status = service.get_session_status(session_id)
    if status is None:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(status)


@wizard_bp.route('/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear all imported data for a wizard session.
    ---
    tags:
      - Wizard
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        description: Wizard session ID to clear
    responses:
      200:
        description: Session cleared
        schema:
          type: object
          properties:
            message:
              type: string
    """
    service.clear_session(session_id)
    return jsonify({'message': 'Session cleared'}), 200
