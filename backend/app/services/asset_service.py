from datetime import datetime, timezone
from app.extensions import db
from app.models.asset import Asset
from app.models.change import AssetChange
from app.errors import NotFoundError, BadRequestError


class AssetService:
    """Service layer for Asset CRUD operations."""

    def find_all(self, session_id='__default__', asset_type=None, status=None,
                 data_classification=None, search=None):
        """Find all assets with optional filters."""
        query = Asset.query.filter_by(session_id=session_id)

        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        if status:
            query = query.filter(Asset.status == status)
        if data_classification:
            query = query.filter(Asset.data_classification == data_classification)
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Asset.name.ilike(search_term),
                    Asset.description.ilike(search_term),
                    Asset.vendor.ilike(search_term),
                    Asset.sub_type.ilike(search_term),
                )
            )

        return query.order_by(Asset.name).all()

    def get_by_id(self, asset_id, session_id='__default__'):
        """Get a single asset by ID."""
        asset = Asset.query.filter_by(id=asset_id, session_id=session_id).first()
        if not asset:
            raise NotFoundError(f'Asset with id {asset_id} not found')
        return asset

    def create(self, data, changed_by='system'):
        """Create a new asset."""
        if not data.get('name'):
            raise BadRequestError('Asset name is required')
        if not data.get('asset_type'):
            raise BadRequestError('Asset type is required')

        asset = Asset(
            asset_type=data['asset_type'],
            sub_type=data.get('sub_type'),
            name=data['name'],
            description=data.get('description'),
            status=data.get('status', 'active'),
            data_classification=data.get('data_classification'),
            security_boundary_id=data.get('security_boundary_id'),
            owner_id=data.get('owner_id'),
            managed_by_id=data.get('managed_by_id'),
            vendor=data.get('vendor'),
            location_id=data.get('location_id'),
            attributes=data.get('attributes'),
            acquired_date=_parse_date(data.get('acquired_date')),
            warranty_expiry=_parse_date(data.get('warranty_expiry')),
            last_audit_date=_parse_date(data.get('last_audit_date')),
            tags=data.get('tags'),
            session_id=data.get('session_id', '__default__'),
        )

        db.session.add(asset)
        db.session.flush()  # get the ID

        # Log the creation
        change = AssetChange(
            asset_id=asset.id,
            changed_by=changed_by,
            change_type='created',
            notes=f'Asset "{asset.name}" created',
            session_id=asset.session_id,
        )
        db.session.add(change)
        db.session.commit()

        return asset

    def update(self, asset_id, data, changed_by='system', session_id='__default__'):
        """Update an existing asset and log changes."""
        asset = self.get_by_id(asset_id, session_id)

        # Track changes for audit log
        tracked_fields = [
            'name', 'asset_type', 'sub_type', 'description', 'status',
            'data_classification', 'security_boundary_id', 'owner_id',
            'managed_by_id', 'vendor', 'location_id', 'tags',
        ]

        for field in tracked_fields:
            if field in data and data[field] != getattr(asset, field):
                old_val = str(getattr(asset, field)) if getattr(asset, field) is not None else None
                new_val = str(data[field]) if data[field] is not None else None

                change_type = 'status_change' if field == 'status' else 'updated'
                change = AssetChange(
                    asset_id=asset.id,
                    changed_by=changed_by,
                    change_type=change_type,
                    field_changed=field,
                    old_value=old_val,
                    new_value=new_val,
                    session_id=session_id,
                )
                db.session.add(change)

        # Apply updates
        updatable_fields = [
            'name', 'asset_type', 'sub_type', 'description', 'status',
            'data_classification', 'security_boundary_id', 'owner_id',
            'managed_by_id', 'vendor', 'location_id', 'attributes', 'tags',
        ]
        for field in updatable_fields:
            if field in data:
                setattr(asset, field, data[field])

        # Handle date fields separately
        date_fields = ['acquired_date', 'warranty_expiry', 'last_audit_date']
        for field in date_fields:
            if field in data:
                setattr(asset, field, _parse_date(data[field]))

        asset.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return asset

    def delete(self, asset_id, session_id='__default__'):
        """Delete an asset and its relationships."""
        asset = self.get_by_id(asset_id, session_id)

        # Delete related changes
        AssetChange.query.filter_by(asset_id=asset_id, session_id=session_id).delete()

        # Delete related relationships (both directions)
        from app.models.asset import AssetRelationship
        AssetRelationship.query.filter(
            db.and_(
                AssetRelationship.session_id == session_id,
                db.or_(
                    AssetRelationship.source_asset_id == asset_id,
                    AssetRelationship.target_asset_id == asset_id,
                )
            )
        ).delete()

        # Delete related licenses
        from app.models.license import License
        License.query.filter_by(software_asset_id=asset_id, session_id=session_id).delete()

        db.session.delete(asset)
        db.session.commit()


def _parse_date(value):
    """Parse a date string (YYYY-MM-DD) or return None."""
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return None
    return value
