import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';

interface Props {
  stage: string;
}

export const LoadingComposition: React.FC<Props> = ({ stage }) => {
  const frame = useCurrentFrame();

  const rotation = (frame / 90) * 360;

  const pulse = interpolate(
    Math.sin((frame / 45) * Math.PI),
    [-1, 1],
    [0.85, 1.15]
  );

  const bars = [24, 18, 30, 15, 22, 28, 12].map((period, i) => {
    const t = (frame + i * 7) % period;
    return interpolate(t, [0, period / 2, period], [0.2, 1, 0.2]);
  });

  const dotCount = Math.floor(frame / 12) % 4;

  const bgGlow = interpolate(frame % 60, [0, 30, 60], [0.08, 0.22, 0.08]);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        background: 'linear-gradient(135deg, #08080e 0%, #0d1117 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Grid overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'linear-gradient(rgba(34,211,238,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(34,211,238,0.04) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
        }}
      />

      {/* Ambient glow */}
      <div
        style={{
          position: 'absolute',
          width: 320,
          height: 320,
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(34,211,238,${bgGlow}) 0%, transparent 70%)`,
        }}
      />

      {/* Orbit ring + dots */}
      <div style={{ position: 'relative', width: 150, height: 150, marginBottom: 28, flexShrink: 0 }}>
        {/* Outer orbit */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '50%',
            border: '1px solid rgba(34,211,238,0.3)',
            transform: `rotate(${rotation}deg)`,
          }}
        >
          <div
            style={{
              position: 'absolute',
              top: -6,
              left: '50%',
              width: 12,
              height: 12,
              borderRadius: '50%',
              background: '#22d3ee',
              transform: 'translateX(-50%)',
              boxShadow: '0 0 14px #22d3ee, 0 0 28px rgba(34,211,238,0.5)',
            }}
          />
        </div>

        {/* Inner orbit (counter) */}
        <div
          style={{
            position: 'absolute',
            inset: 24,
            borderRadius: '50%',
            border: '1px solid rgba(34,211,238,0.12)',
            transform: `rotate(${-rotation * 0.6}deg)`,
          }}
        >
          <div
            style={{
              position: 'absolute',
              bottom: -5,
              left: '50%',
              width: 9,
              height: 9,
              borderRadius: '50%',
              background: 'rgba(34,211,238,0.65)',
              transform: 'translateX(-50%)',
              boxShadow: '0 0 8px rgba(34,211,238,0.7)',
            }}
          />
        </div>

        {/* Center pulse glow */}
        <div
          style={{
            position: 'absolute',
            inset: 48,
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(34,211,238,0.28), rgba(6,182,212,0.08))',
            transform: `scale(${pulse})`,
            boxShadow: '0 0 28px rgba(34,211,238,0.2)',
          }}
        />

        {/* Analytics icon */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none">
            <path
              d="M3 17l4-8 4 4 4-6 4 10H3z"
              stroke="#22d3ee"
              strokeWidth="1.5"
              strokeLinejoin="round"
              fill="rgba(34,211,238,0.1)"
            />
          </svg>
        </div>
      </div>

      {/* EQ bars */}
      <div style={{ display: 'flex', gap: 5, alignItems: 'flex-end', height: 36, marginBottom: 26 }}>
        {bars.map((h, i) => (
          <div
            key={i}
            style={{
              width: 7,
              height: `${h * 100}%`,
              background: `rgba(34,211,238,${0.2 + h * 0.8})`,
              borderRadius: 3,
            }}
          />
        ))}
      </div>

      {/* Stage label */}
      <div
        style={{
          fontSize: 15,
          fontWeight: 600,
          color: '#22d3ee',
          letterSpacing: '0.02em',
          marginBottom: 8,
          textAlign: 'center',
          padding: '0 24px',
        }}
      >
        {stage}
        {'.'.repeat(dotCount)}
      </div>

      {/* Sub-label */}
      <div
        style={{
          fontSize: 10,
          color: 'rgba(255,255,255,0.22)',
          letterSpacing: '0.14em',
          textTransform: 'uppercase',
        }}
      >
        AI-Powered Social Analysis
      </div>
    </div>
  );
};
