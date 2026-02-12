import csv
import io
import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.models.wizard_import import WizardImport, WizardSession

# Entity type definitions with required columns and descriptions
ENTITY_TYPES = {
    'assets': {
        'required': ['name', 'asset_type'],
        'description': 'Assets with name, asset_type (hardware/software/cloud_service/network/contract), sub_type, status, data_classification, vendor, description',
        'sample': 'name,asset_type,sub_type,status,data_classification,vendor,description\nPROD-SVR-01,hardware,server,active,CUI,Dell,Production Server 1\nMission App v3.2,software,custom_app,active,CUI,,Custom Java/Spring Boot application',
    },
    'people': {
        'required': ['name'],
        'description': 'People with name, email, role, team, phone',
        'sample': 'name,email,role,team,phone\nSarah Chen,sarah.chen@company.com,IT Director,IT Leadership,555-0101\nMarcus Johnson,marcus.johnson@company.com,Sr System Admin,Infrastructure,555-0102',
    },
    'locations': {
        'required': ['name'],
        'description': 'Locations with name, location_type (data_center/office/cloud_region/colo), address, notes',
        'sample': 'name,location_type,address,notes\nReston Main Office,office,"11955 Democracy Dr, Reston, VA 20190",Main corporate HQ\nAWS GovCloud US-East,cloud_region,us-gov-east-1,FedRAMP High authorized',
    },
    'security_boundaries': {
        'required': ['name'],
        'description': 'Security boundaries with name, boundary_type (cui_boundary/fci_boundary/corporate), description, cmmc_level (level_1/level_2/level_3), assessment_date',
        'sample': 'name,boundary_type,description,cmmc_level,assessment_date\nCUI Enclave,cui_boundary,Controlled Unclassified Information boundary,level_2,2025-09-15\nCorporate Network,corporate,Standard corporate network,level_1,2025-06-01',
    },
    'licenses': {
        'required': ['software_name', 'vendor'],
        'description': 'Licenses with software_name (matches asset name), license_type (perpetual/subscription/per_seat/site), vendor, total_seats, used_seats, cost_per_period, billing_period, start_date, expiry_date, auto_renew, contract_number',
        'sample': 'software_name,license_type,vendor,total_seats,used_seats,cost_per_period,billing_period,start_date,expiry_date,auto_renew,contract_number\nMicrosoft 365 GCC,per_seat,Microsoft,15,12,22,monthly,2025-01-01,2026-12-31,true,MS-GOV-2025-001',
    },
    'relationships': {
        'required': ['source_asset', 'target_asset', 'relationship_type'],
        'description': 'Asset relationships with source_asset (name), target_asset (name), relationship_type (runs/depends_on/supports/assigned_to/licensed_under/installed_on/protects/within_boundary), description',
        'sample': 'source_asset,target_asset,relationship_type,description\nPROD-SVR-01,Mission App v3.2,runs,Production server runs mission app\nMission App v3.2,PostgreSQL 15,depends_on,App depends on database',
    },
}


class WizardService:
    """Service for handling wizard-based data imports."""

    def create_session(self):
        """Create a new wizard session."""
        session_id = str(uuid.uuid4())
        ws = WizardSession(session_id=session_id)
        db.session.add(ws)
        db.session.commit()
        return {'session_id': session_id, 'created_at': ws.created_at.isoformat()}

    def get_entity_types(self):
        """Return available entity types with metadata."""
        return {
            k: {'required': v['required'], 'description': v['description']}
            for k, v in ENTITY_TYPES.items()
        }

    def get_sample(self, entity_type):
        """Return sample CSV for an entity type."""
        et = ENTITY_TYPES.get(entity_type)
        if not et:
            return None
        return et['sample']

    def parse_csv_text(self, text):
        """Parse pasted CSV or TSV text into list of dicts."""
        text = text.strip()
        if not text:
            return []

        # Auto-detect delimiter
        first_line = text.split('\n')[0]
        if '\t' in first_line:
            delimiter = '\t'
        else:
            delimiter = ','

        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        rows = []
        for row in reader:
            # Strip whitespace from keys and values
            cleaned = {k.strip(): (v.strip() if v else '') for k, v in row.items() if k}
            rows.append(cleaned)
        return rows

    def parse_file(self, file_storage):
        """Parse an uploaded CSV or Excel file into list of dicts."""
        filename = file_storage.filename or ''

        if filename.endswith('.csv') or filename.endswith('.tsv'):
            text = file_storage.read().decode('utf-8')
            return self.parse_csv_text(text)

        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            import openpyxl
            wb = openpyxl.load_workbook(file_storage, read_only=True, data_only=True)
            ws = wb.active
            rows_iter = ws.iter_rows(values_only=True)
            headers = [str(h).strip() if h else '' for h in next(rows_iter)]
            rows = []
            for row_vals in rows_iter:
                row_dict = {}
                for i, val in enumerate(row_vals):
                    if i < len(headers) and headers[i]:
                        row_dict[headers[i]] = str(val).strip() if val is not None else ''
                rows.append(row_dict)
            wb.close()
            return rows

        return []

    def validate_rows(self, entity_type, rows):
        """Validate rows against required columns for the entity type."""
        et = ENTITY_TYPES.get(entity_type)
        if not et:
            return [], [f'Unknown entity type: {entity_type}']

        required = et['required']
        errors = []
        valid_rows = []

        if not rows:
            return [], ['No data rows provided']

        # Check that required columns exist in the first row
        if rows:
            available_cols = set(rows[0].keys())
            missing = [c for c in required if c not in available_cols]
            if missing:
                return [], [f'Missing required columns: {", ".join(missing)}']

        for i, row in enumerate(rows):
            row_errors = []
            for col in required:
                val = row.get(col, '')
                if not val or str(val).strip() == '':
                    row_errors.append(f'Row {i + 1}: missing required value for "{col}"')
            if row_errors:
                errors.extend(row_errors)
            else:
                valid_rows.append(row)

        return valid_rows, errors

    def import_entity(self, session_id, entity_type, rows):
        """Import rows into the staging table for a given entity type.

        Replaces any existing rows for this session + entity_type (idempotent).
        """
        # Validate session exists
        ws = WizardSession.query.filter_by(session_id=session_id).first()
        if not ws:
            return {'imported': 0, 'errors': ['Invalid session_id'], 'total': 0}

        valid_rows, errors = self.validate_rows(entity_type, rows)

        # Delete existing rows for this session + entity_type (idempotent re-import)
        WizardImport.query.filter_by(
            session_id=session_id, entity_type=entity_type
        ).delete()

        # Insert valid rows
        for i, row in enumerate(valid_rows):
            wi = WizardImport(
                session_id=session_id,
                entity_type=entity_type,
                row_data=row,
                row_index=i,
            )
            db.session.add(wi)

        ws.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return {
            'imported': len(valid_rows),
            'errors': errors[:20],  # cap at 20 errors
            'total': len(rows),
        }

    def get_preview(self, session_id, entity_type, limit=50):
        """Return imported rows for preview."""
        rows = WizardImport.query.filter_by(
            session_id=session_id, entity_type=entity_type
        ).order_by(WizardImport.row_index).limit(limit).all()
        return [r.row_data for r in rows]

    def get_session_status(self, session_id):
        """Return counts per entity type for this session."""
        ws = WizardSession.query.filter_by(session_id=session_id).first()
        if not ws:
            return None

        counts = db.session.query(
            WizardImport.entity_type,
            db.func.count(WizardImport.id)
        ).filter_by(session_id=session_id).group_by(
            WizardImport.entity_type
        ).all()

        return {
            'session_id': session_id,
            'created_at': ws.created_at.isoformat(),
            'updated_at': ws.updated_at.isoformat() if ws.updated_at else None,
            'entities': {et: count for et, count in counts},
            'total_rows': sum(c for _, c in counts),
        }

    def clear_session(self, session_id):
        """Delete all staged data for a session."""
        WizardImport.query.filter_by(session_id=session_id).delete()
        WizardSession.query.filter_by(session_id=session_id).delete()
        db.session.commit()
