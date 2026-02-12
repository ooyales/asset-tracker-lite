import { useRef, useEffect, useCallback } from 'react';
import * as d3 from 'd3';
import type { GraphNode, GraphLink, AssetType } from '@/types';

const TYPE_COLORS: Record<AssetType, string> = {
  hardware: '#337ab7',
  software: '#5cb85c',
  cloud: '#7c3aed',
  network: '#f0ad4e',
};

const NODE_RADIUS = 20;

interface RelationshipGraphProps {
  nodes: GraphNode[];
  links: GraphLink[];
  width: number;
  height: number;
  onNodeClick?: (node: GraphNode) => void;
  selectedNodeId?: string | null;
}

export default function RelationshipGraph({
  nodes,
  links,
  width,
  height,
  onNodeClick,
  selectedNodeId,
}: RelationshipGraphProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  const drawGraph = useCallback(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Root group for zoom/pan
    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Deep-copy data to avoid mutation issues
    const nodesCopy: GraphNode[] = nodes.map((n) => ({ ...n }));
    const linksCopy: GraphLink[] = links.map((l) => ({
      ...l,
      source: typeof l.source === 'string' ? l.source : l.source.id,
      target: typeof l.target === 'string' ? l.target : l.target.id,
    }));

    // Build simulation
    const simulation = d3
      .forceSimulation<GraphNode>(nodesCopy)
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphLink>(linksCopy)
          .id((d) => d.id)
          .distance(120)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(NODE_RADIUS + 10));

    simulationRef.current = simulation;

    // Arrow marker
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', NODE_RADIUS + 10)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Links
    const link = g
      .append('g')
      .selectAll<SVGLineElement, GraphLink>('line')
      .data(linksCopy)
      .join('line')
      .attr('stroke', '#ccc')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)');

    // Link labels
    const linkLabel = g
      .append('g')
      .selectAll<SVGTextElement, GraphLink>('text')
      .data(linksCopy)
      .join('text')
      .text((d) => d.relationship_type)
      .attr('font-size', 9)
      .attr('fill', '#999')
      .attr('text-anchor', 'middle')
      .attr('dy', -4);

    // Node groups
    const node = g
      .append('g')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(nodesCopy)
      .join('g')
      .attr('cursor', 'pointer')
      .call(
        d3
          .drag<SVGGElement, GraphNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Node circles
    node
      .append('circle')
      .attr('r', NODE_RADIUS)
      .attr('fill', (d) => TYPE_COLORS[d.asset_type] || '#999')
      .attr('stroke', (d) =>
        selectedNodeId && d.id === selectedNodeId ? '#333' : '#fff'
      )
      .attr('stroke-width', (d) =>
        selectedNodeId && d.id === selectedNodeId ? 3 : 2
      )
      .attr('opacity', (d) => {
        if (!selectedNodeId) return 1;
        // Check if this node is selected or connected
        const isConnected = linksCopy.some(
          (l) =>
            (typeof l.source === 'object' ? l.source.id : l.source) === selectedNodeId &&
            (typeof l.target === 'object' ? l.target.id : l.target) === d.id ||
            (typeof l.target === 'object' ? l.target.id : l.target) === selectedNodeId &&
            (typeof l.source === 'object' ? l.source.id : l.source) === d.id
        );
        return d.id === selectedNodeId || isConnected ? 1 : 0.3;
      });

    // Node labels
    node
      .append('text')
      .text((d) => d.name.length > 14 ? d.name.slice(0, 12) + '...' : d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', NODE_RADIUS + 14)
      .attr('font-size', 10)
      .attr('fill', '#333')
      .attr('font-weight', 500);

    // Click handler
    node.on('click', (_event, d) => {
      if (onNodeClick) onNodeClick(d);
    });

    // Highlight connected links
    link.attr('opacity', (d) => {
      if (!selectedNodeId) return 0.6;
      const src = typeof d.source === 'object' ? d.source.id : d.source;
      const tgt = typeof d.target === 'object' ? d.target.id : d.target;
      return src === selectedNodeId || tgt === selectedNodeId ? 1 : 0.15;
    });

    link.attr('stroke', (d) => {
      if (!selectedNodeId) return '#ccc';
      const src = typeof d.source === 'object' ? d.source.id : d.source;
      const tgt = typeof d.target === 'object' ? d.target.id : d.target;
      return src === selectedNodeId || tgt === selectedNodeId ? '#666' : '#eee';
    });

    // Tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as GraphNode).x || 0)
        .attr('y1', (d) => (d.source as GraphNode).y || 0)
        .attr('x2', (d) => (d.target as GraphNode).x || 0)
        .attr('y2', (d) => (d.target as GraphNode).y || 0);

      linkLabel
        .attr('x', (d) =>
          ((d.source as GraphNode).x! + (d.target as GraphNode).x!) / 2
        )
        .attr('y', (d) =>
          ((d.source as GraphNode).y! + (d.target as GraphNode).y!) / 2
        );

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    // Initial zoom to fit
    const initialTransform = d3.zoomIdentity.translate(0, 0).scale(0.9);
    svg.call(zoom.transform, initialTransform);
  }, [nodes, links, width, height, onNodeClick, selectedNodeId]);

  useEffect(() => {
    drawGraph();
    return () => {
      simulationRef.current?.stop();
    };
  }, [drawGraph]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      className="bg-white rounded"
      style={{ border: '1px solid #ddd' }}
    />
  );
}
