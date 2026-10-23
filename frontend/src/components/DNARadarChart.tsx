import React from 'react';

interface DNARadarChartProps {
  data: Record<string, number>;
  compareData?: Record<string, number>;
  labels?: Record<string, string>;
  size?: number;
  labelColor?: string;
  fillColor?: string;
  compareColor?: string;
}

const DEFAULT_LABELS: Record<string, string> = {
  temporal_dynamics: 'Time Pattern',
  time_pattern: 'Time Pattern',
  crime_characteristics: 'Crime Type',
  location_and_environment: 'Location',
  location_context: 'Location',
  method_and_activity: 'Method/Weapon',
  weapon_method_context: 'Method/Weapon',
  people_and_demographics: 'People/Context',
  people_context: 'People/Context',
  property_and_economics: 'Property',
  property_context: 'Property',
  context_and_harm: 'Harm/Injury',
  harm_context: 'Harm/Injury',
};

const CANONICAL_AXES = [
  'temporal_dynamics',
  'crime_characteristics',
  'location_and_environment',
  'method_and_activity',
  'people_and_demographics',
  'property_and_economics',
  'context_and_harm',
];

export const DNARadarChart: React.FC<DNARadarChartProps> = ({
  data,
  compareData,
  labels = DEFAULT_LABELS,
  size = 320,
  fillColor = 'rgba(14, 165, 233, 0.45)',
  compareColor = 'rgba(244, 63, 94, 0.45)',
}) => {
  const center = size / 2;
  const radius = size * 0.38;

  // Align axes canonically so radar geometry is consistent and stable
  const rawKeys = Object.keys(data || {});
  const hasCanonicalKey = CANONICAL_AXES.some((k) => (data && k in data) || (compareData && k in compareData));

  const keys = hasCanonicalKey
    ? [
        ...CANONICAL_AXES.filter((k) => (data && k in data) || (compareData && k in compareData)),
        ...rawKeys.filter((k) => !CANONICAL_AXES.includes(k)),
      ]
    : rawKeys;

  if (keys.length === 0) return null;

  const totalAxes = keys.length;
  const angleSlice = (Math.PI * 2) / totalAxes;

  // Compute vertices for polygon with defensive value sanitization
  const getCoordinates = (value: unknown, index: number) => {
    const num = typeof value === 'number' && Number.isFinite(value) ? value : 0;
    // Normalize value to 0-1 range (supports raw L2 norm [0, 1] or percentage [0, 100])
    const normValue = num > 1.0 ? Math.min(1.0, Math.max(0.0, num / 100.0)) : Math.max(0.0, Math.min(1.0, num));
    const r = radius * normValue;
    const angle = angleSlice * index - Math.PI / 2;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  const primaryPoints = keys
    .map((k, i) => {
      const coord = getCoordinates(data ? data[k] : 0, i);
      return `${coord.x},${coord.y}`;
    })
    .join(' ');

  const comparePoints = compareData
    ? keys
        .map((k, i) => {
          const coord = getCoordinates(compareData[k], i);
          return `${coord.x},${coord.y}`;
        })
        .join(' ')
    : null;

  // Concentric background rings (25%, 50%, 75%, 100%)
  const levels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background grid rings */}
        {levels.map((level, idx) => (
          <circle
            key={idx}
            cx={center}
            cy={center}
            r={radius * level}
            fill="none"
            stroke="var(--border-subtle)"
            strokeDasharray={idx === levels.length - 1 ? 'none' : '3 3'}
            strokeWidth="1"
          />
        ))}

        {/* Axis radial lines */}
        {keys.map((k, i) => {
          const angle = angleSlice * i - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          const labelX = center + (radius + 22) * Math.cos(angle);
          const labelY = center + (radius + 22) * Math.sin(angle);
          const displayLabel = labels[k] || k.replace(/_/g, ' ');

          return (
            <g key={i}>
              <line x1={center} y1={center} x2={x} y2={y} stroke="var(--border-subtle)" strokeWidth="1" />
              <text
                x={labelX}
                y={labelY}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="10"
                fill="var(--text-muted)"
                fontFamily="var(--font-sans)"
                fontWeight="500"
              >
                {displayLabel}
              </text>
            </g>
          );
        })}

        {/* Comparison polygon (if comparing two incidents) */}
        {comparePoints && (
          <polygon
            points={comparePoints}
            fill={compareColor}
            stroke="#f43f5e"
            strokeWidth="2"
            strokeOpacity="0.8"
          />
        )}

        {/* Primary polygon */}
        <polygon
          points={primaryPoints}
          fill={fillColor}
          stroke="var(--accent-cyan)"
          strokeWidth="2"
          strokeOpacity="0.9"
        />

        {/* Data points */}
        {keys.map((k, i) => {
          const coord = getCoordinates(data[k] || 0, i);
          return (
            <circle
              key={i}
              cx={coord.x}
              cy={coord.y}
              r="3.5"
              fill="var(--accent-cyan)"
              stroke="#080c14"
              strokeWidth="1.5"
            />
          );
        })}
      </svg>

      {/* Legend if comparing */}
      {compareData && (
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', marginTop: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', background: 'var(--accent-cyan)', borderRadius: '2px' }}></span>
            <span>Query Incident</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', background: '#f43f5e', borderRadius: '2px' }}></span>
            <span>Matched Incident</span>
          </div>
        </div>
      )}
    </div>
  );
};
