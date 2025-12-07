"use client";
import { motion } from 'framer-motion';
import { IconType } from 'react-icons';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: IconType;
  color: string;
}

export default function StatsCard({ title, value, icon: Icon, color }: StatsCardProps) {
  return (
    <motion.div
      className="glass-panel"
      whileHover={{ y: -5 }}
      style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: '15px' }}
    >
      <div style={{
        padding: '12px',
        borderRadius: '12px',
        background: `rgba(${color}, 0.1)`,
        color: `rgb(${color})`
      }}>
        <Icon size={24} />
      </div>
      <div>
        <h3 style={{ margin: 0, fontSize: '0.9rem', color: '#888' }}>{title}</h3>
        <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold' }}>{value}</p>
      </div>
    </motion.div>
  );
}