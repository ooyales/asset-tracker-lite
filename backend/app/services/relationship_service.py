import networkx as nx
from collections import deque
from app.extensions import db
from app.models.asset import Asset, AssetRelationship
from app.errors import NotFoundError


# Color mapping for asset types in D3 visualization
ASSET_TYPE_COLORS = {
    'hardware': '#3b82f6',      # blue
    'software': '#10b981',      # emerald
    'cloud_service': '#8b5cf6', # violet
    'license': '#f59e0b',       # amber
    'network': '#ef4444',       # red
    'contract': '#6366f1',      # indigo
}

# D3 group IDs for asset types
ASSET_TYPE_GROUPS = {
    'hardware': 1,
    'software': 2,
    'cloud_service': 3,
    'license': 4,
    'network': 5,
    'contract': 6,
}


class RelationshipService:
    """Service for relationship operations using NetworkX for graph analysis."""

    def build_graph(self, session_id='__default__'):
        """Build a NetworkX directed graph from asset relationships."""
        G = nx.DiGraph()

        # Add all assets as nodes
        assets = Asset.query.filter_by(session_id=session_id).all()
        for asset in assets:
            G.add_node(asset.id, name=asset.name, asset_type=asset.asset_type,
                       sub_type=asset.sub_type, status=asset.status)

        # Add relationships as edges
        rels = AssetRelationship.query.filter_by(session_id=session_id).all()
        for rel in rels:
            G.add_edge(rel.source_asset_id, rel.target_asset_id,
                       relationship_type=rel.relationship_type,
                       description=rel.description,
                       id=rel.id)

        return G

    def get_graph_json(self, session_id='__default__'):
        """Return D3-compatible JSON representation of the asset graph."""
        assets = Asset.query.filter_by(session_id=session_id).all()
        rels = AssetRelationship.query.filter_by(session_id=session_id).all()

        nodes = []
        for asset in assets:
            nodes.append({
                'id': asset.id,
                'name': asset.name,
                'type': asset.asset_type,
                'sub_type': asset.sub_type,
                'status': asset.status,
                'group': ASSET_TYPE_GROUPS.get(asset.asset_type, 0),
                'color': ASSET_TYPE_COLORS.get(asset.asset_type, '#6b7280'),
                'data_classification': asset.data_classification,
            })

        links = []
        for rel in rels:
            links.append({
                'source': rel.source_asset_id,
                'target': rel.target_asset_id,
                'type': rel.relationship_type,
                'description': rel.description,
                'id': rel.id,
            })

        return {'nodes': nodes, 'links': links}

    def get_impact(self, asset_id, session_id='__default__', depth=2):
        """BFS to find downstream dependencies from a given asset.

        Returns assets that are impacted if the source asset has an issue.
        Follows edges in the outgoing direction (source -> target).
        """
        G = self.build_graph(session_id)

        if asset_id not in G:
            raise NotFoundError(f'Asset {asset_id} not found in graph')

        # BFS with depth tracking
        visited = {}
        queue = deque([(asset_id, 0)])

        while queue:
            current, current_depth = queue.popleft()
            if current in visited:
                continue
            visited[current] = current_depth

            if current_depth < depth:
                for successor in G.successors(current):
                    if successor not in visited:
                        queue.append((successor, current_depth + 1))

        # Build results (exclude the source asset itself)
        impacted = []
        for node_id, node_depth in visited.items():
            if node_id == asset_id:
                continue
            node_data = G.nodes[node_id]
            impacted.append({
                'id': node_id,
                'name': node_data.get('name'),
                'asset_type': node_data.get('asset_type'),
                'status': node_data.get('status'),
                'depth': node_depth,
            })

        # Also include the relationship path info
        source_data = G.nodes[asset_id]
        return {
            'source': {
                'id': asset_id,
                'name': source_data.get('name'),
                'asset_type': source_data.get('asset_type'),
            },
            'depth_limit': depth,
            'impacted_count': len(impacted),
            'impacted': sorted(impacted, key=lambda x: (x['depth'], x['name'])),
        }

    def get_orphans(self, session_id='__default__'):
        """Find assets with no relationships (neither incoming nor outgoing)."""
        G = self.build_graph(session_id)

        orphans = []
        for node_id in G.nodes:
            if G.degree(node_id) == 0:
                node_data = G.nodes[node_id]
                orphans.append({
                    'id': node_id,
                    'name': node_data.get('name'),
                    'asset_type': node_data.get('asset_type'),
                    'status': node_data.get('status'),
                })

        return orphans

    def create_relationship(self, data):
        """Create a new asset relationship."""
        rel = AssetRelationship(
            source_asset_id=data['source_asset_id'],
            target_asset_id=data['target_asset_id'],
            relationship_type=data['relationship_type'],
            description=data.get('description'),
            session_id=data.get('session_id', '__default__'),
        )
        db.session.add(rel)
        db.session.commit()
        return rel

    def delete_relationship(self, rel_id, session_id='__default__'):
        """Delete a relationship by ID."""
        rel = AssetRelationship.query.filter_by(id=rel_id, session_id=session_id).first()
        if not rel:
            raise NotFoundError(f'Relationship {rel_id} not found')
        db.session.delete(rel)
        db.session.commit()
