import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, Server, Monitor, Cloud, Wifi } from 'lucide-react';
import RelationshipGraph from '@/components/charts/RelationshipGraph';
import { relationshipsApi } from '@/api/relationships';
import type { GraphNode, GraphLink, GraphData, AssetType } from '@/types';

/* ── Mock graph data ────────────────────────────────────────────────── */
const MOCK_GRAPH: GraphData = {
  nodes: [
    { id: '1', name: 'Prod-DB-01', asset_type: 'hardware', status: 'active' },
    { id: '2', name: 'Auth-Lambda', asset_type: 'cloud', status: 'active' },
    { id: '3', name: 'Firewall-Edge-01', asset_type: 'network', status: 'active' },
    { id: '4', name: 'Microsoft 365', asset_type: 'software', status: 'active' },
    { id: '5', name: 'Dev-WS-22', asset_type: 'hardware', status: 'active' },
    { id: '6', name: 'VPN-Concentrator', asset_type: 'network', status: 'maintenance' },
    { id: '7', name: 'Splunk SIEM', asset_type: 'software', status: 'active' },
    { id: '8', name: 'Azure-VNET', asset_type: 'cloud', status: 'active' },
    { id: '9', name: 'Legacy-ERP', asset_type: 'hardware', status: 'retired' },
    { id: '10', name: 'Core-Switch-01', asset_type: 'network', status: 'active' },
    { id: '11', name: 'Jira Cloud', asset_type: 'software', status: 'active' },
    { id: '12', name: 'S3-Backup', asset_type: 'cloud', status: 'active' },
  ],
  links: [
    { source: '2', target: '1', relationship_type: 'connects_to' },
    { source: '1', target: '3', relationship_type: 'protected_by' },
    { source: '1', target: '7', relationship_type: 'monitored_by' },
    { source: '5', target: '4', relationship_type: 'runs' },
    { source: '5', target: '11', relationship_type: 'uses' },
    { source: '6', target: '3', relationship_type: 'connects_to' },
    { source: '8', target: '2', relationship_type: 'hosts' },
    { source: '10', target: '1', relationship_type: 'connects_to' },
    { source: '10', target: '6', relationship_type: 'connects_to' },
    { source: '7', target: '3', relationship_type: 'monitors' },
    { source: '1', target: '12', relationship_type: 'backed_up_to' },
    { source: '9', target: '1', relationship_type: 'replaced_by' },
  ],
};

const TYPE_INFO: { type: AssetType; color: string; icon: React.ReactNode; label: string }[] = [
  { type: 'hardware', color: '#337ab7', icon: <Server size={12} />, label: 'Hardware' },
  { type: 'software', color: '#5cb85c', icon: <Monitor size={12} />, label: 'Software' },
  { type: 'cloud', color: '#7c3aed', icon: <Cloud size={12} />, label: 'Cloud' },
  { type: 'network', color: '#f0ad4e', icon: <Wifi size={12} />, label: 'Network' },
];

export default function RelationshipMapPage() {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<GraphData>(MOCK_GRAPH);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [typeFilter, setTypeFilter] = useState<AssetType | ''>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [dimensions, setDimensions] = useState({ width: 900, height: 550 });

  // Fetch real data
  useEffect(() => {
    relationshipsApi
      .getGraph(typeFilter ? { asset_type: typeFilter } : undefined)
      .then(setGraphData)
      .catch(() => {
        /* keep mock */
      });
  }, [typeFilter]);

  // Resize observer
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: Math.max(entry.contentRect.height, 500),
        });
      }
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Filter nodes/links
  const filteredNodes = graphData.nodes.filter((n) => {
    if (typeFilter && n.asset_type !== typeFilter) return false;
    if (searchQuery && !n.name.toLowerCase().includes(searchQuery.toLowerCase()))
      return false;
    return true;
  });

  const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));

  const filteredLinks = graphData.links.filter((l) => {
    const src = typeof l.source === 'string' ? l.source : l.source.id;
    const tgt = typeof l.target === 'string' ? l.target : l.target.id;
    return filteredNodeIds.has(src) && filteredNodeIds.has(tgt);
  });

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(selectedNode?.id === node.id ? null : node);
  };

  // Get connections for selected node
  const connections = selectedNode
    ? graphData.links
        .filter((l) => {
          const src = typeof l.source === 'string' ? l.source : l.source.id;
          const tgt = typeof l.target === 'string' ? l.target : l.target.id;
          return src === selectedNode.id || tgt === selectedNode.id;
        })
        .map((l) => {
          const src = typeof l.source === 'string' ? l.source : l.source.id;
          const tgt = typeof l.target === 'string' ? l.target : l.target.id;
          const connectedId = src === selectedNode.id ? tgt : src;
          const connectedNode = graphData.nodes.find((n) => n.id === connectedId);
          const direction = src === selectedNode.id ? 'outgoing' : 'incoming';
          return {
            node: connectedNode,
            relationship_type: l.relationship_type,
            direction,
          };
        })
    : [];

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)]">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-xl font-bold text-eaw-font">Relationship Map</h1>
        <p className="text-sm text-eaw-muted mt-1">
          Explore asset relationships and dependencies.{' '}
          {filteredNodes.length} nodes, {filteredLinks.length} connections.
        </p>
      </div>

      {/* Controls */}
      <div className="eaw-card mb-4">
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value as AssetType | '');
              setSelectedNode(null);
            }}
            className="select-field"
          >
            <option value="">All Types</option>
            <option value="hardware">Hardware</option>
            <option value="software">Software</option>
            <option value="cloud">Cloud</option>
            <option value="network">Network</option>
          </select>

          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-eaw-muted"
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter nodes..."
              className="input-field pl-8"
            />
          </div>

          {selectedNode && (
            <button
              className="btn-secondary text-xs"
              onClick={() => setSelectedNode(null)}
            >
              <X size={14} />
              Clear selection
            </button>
          )}
        </div>
      </div>

      {/* Graph + Detail Panel */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Graph */}
        <div
          ref={containerRef}
          className="flex-1 bg-white rounded shadow-eaw overflow-hidden"
        >
          <RelationshipGraph
            nodes={filteredNodes}
            links={filteredLinks}
            width={dimensions.width}
            height={dimensions.height}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedNode?.id ?? null}
          />
        </div>

        {/* Detail Panel */}
        {selectedNode && (
          <div className="w-72 bg-white rounded shadow-eaw p-4 overflow-y-auto flex-shrink-0">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-eaw-font">{selectedNode.name}</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-eaw-muted hover:text-eaw-font"
              >
                <X size={14} />
              </button>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-eaw-muted">Type:</span>
                <span className="badge-info">{selectedNode.asset_type}</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-eaw-muted">Status:</span>
                <span
                  className={
                    selectedNode.status === 'active'
                      ? 'badge-success'
                      : selectedNode.status === 'maintenance'
                      ? 'badge-warning'
                      : 'badge-muted'
                  }
                >
                  {selectedNode.status}
                </span>
              </div>
            </div>

            <button
              className="btn-primary w-full text-xs mb-4 justify-center"
              onClick={() => navigate(`/assets/${selectedNode.id}`)}
            >
              View Asset Details
            </button>

            <h4 className="text-xs font-semibold uppercase text-eaw-muted tracking-wide mb-2">
              Connections ({connections.length})
            </h4>
            <div className="space-y-2">
              {connections.map((conn, idx) => (
                <div
                  key={idx}
                  className="p-2 bg-gray-50 rounded border border-eaw-border-light text-xs cursor-pointer hover:bg-gray-100"
                  onClick={() => {
                    if (conn.node) {
                      setSelectedNode(conn.node);
                    }
                  }}
                >
                  <div className="font-medium text-eaw-font">
                    {conn.node?.name ?? 'Unknown'}
                  </div>
                  <div className="text-eaw-muted mt-0.5">
                    <span className="badge-muted mr-1">{conn.direction}</span>
                    {conn.relationship_type}
                  </div>
                </div>
              ))}
              {connections.length === 0 && (
                <p className="text-xs text-eaw-muted">No connections.</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-3 flex items-center gap-4 justify-center">
        {TYPE_INFO.map((t) => (
          <div key={t.type} className="flex items-center gap-1.5 text-xs text-eaw-font">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: t.color }}
            />
            {t.icon}
            <span>{t.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
