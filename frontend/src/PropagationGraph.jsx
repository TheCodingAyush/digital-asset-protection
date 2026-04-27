import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import './propagation.css';

const CENTER_X = 400;
const CENTER_Y = 0;
const CHILD_Y = 220;
const H_SPACING = 200;

const PropagationGraph = ({ matches = [] }) => {
  const { nodes, edges } = useMemo(() => {
    if (!matches.length) return { nodes: [], edges: [] };

    const totalWidth = (matches.length - 1) * H_SPACING;
    const startX = CENTER_X - totalWidth / 2;

    const centerNode = {
      id: 'center',
      position: { x: CENTER_X - 70, y: CENTER_Y },
      data: { label: 'YOUR CONTENT' },
      style: {
        background: '#FF3D00',
        color: '#0A0A0A',
        fontWeight: 700,
        border: 'none',
        borderRadius: 0,
        padding: '12px 20px',
        fontSize: '0.75rem',
        letterSpacing: '0.1em',
        fontFamily: "'Inter Tight', sans-serif",
        textTransform: 'uppercase',
        minWidth: 140,
        textAlign: 'center',
      },
    };

    const childNodes = matches.map((match, idx) => {
      const isYouTube = match.source === 'YouTube';
      const title = (match.title || match.id || 'Unknown').slice(0, 30);
      const sim = match.similarity != null ? `${(match.similarity * 100).toFixed(1)}%` : '—';
      const source = match.source || 'Unknown';

      return {
        id: `match-${idx}`,
        position: { x: startX + idx * H_SPACING - 70, y: CHILD_Y },
        data: {
          label: (
            <div className="pg-node-content">
              <div className="pg-node-title">{title}{(match.title || '').length > 30 ? '…' : ''}</div>
              <div className="pg-node-sim">{sim}</div>
              <div className={`pg-node-source ${isYouTube ? 'pg-source-yt' : 'pg-source-ds'}`}>{source}</div>
            </div>
          ),
        },
        style: {
          background: '#0F0F0F',
          border: `2px solid ${isYouTube ? '#ff0000' : '#262626'}`,
          color: '#FAFAFA',
          borderRadius: 0,
          padding: '10px 14px',
          fontFamily: "'Inter Tight', sans-serif",
          fontSize: '0.75rem',
          minWidth: 140,
        },
      };
    });

    const childEdges = matches.map((match, idx) => {
      const isYouTube = match.source === 'YouTube';
      return {
        id: `edge-${idx}`,
        source: 'center',
        target: `match-${idx}`,
        style: {
          stroke: isYouTube ? '#ff0000' : '#262626',
          strokeWidth: 2,
        },
        animated: isYouTube,
      };
    });

    return { nodes: [centerNode, ...childNodes], edges: childEdges };
  }, [matches]);

  if (!matches.length) return null;

  return (
    <div className="pg-wrapper">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        panOnDrag={true}
        zoomOnScroll={true}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#262626" variant="dots" gap={20} size={1} />
        <Controls className="pg-controls" showInteractive={false} />
      </ReactFlow>
    </div>
  );
};

export default PropagationGraph;
