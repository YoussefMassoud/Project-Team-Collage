"use client";
import { motion } from 'framer-motion';
import { Play, FileAudio } from 'lucide-react';

export default function Report() {
    return (
        <div className="container">
            <motion.h1
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ fontSize: '2rem', marginBottom: '30px' }}
            >
                AI <span className="gradient-text">Report</span>
            </motion.h1>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
                <motion.div className="glass-panel" style={{ padding: '20px', aspectRatio: '16/9', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#000', position: 'relative', overflow: 'hidden' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(45deg, #7c3aed, #db2777)', opacity: 0.2 }} />
                    <div style={{ zIndex: 1, textAlign: 'center' }}>
                        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'rgba(255,255,255,0.2)', display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '0 auto 20px', cursor: 'pointer', backdropFilter: 'blur(5px)' }}>
                            <Play size={40} fill="white" />
                        </div>
                        <p>Play AI Video Analysis</p>
                    </div>
                </motion.div>

                <motion.div className="glass-panel" style={{ padding: '30px' }} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                    <h3 style={{ marginTop: 0 }}>Executive Summary</h3>
                    <p style={{ lineHeight: '1.8', color: '#ccc' }}>
                        Based on the analysis of your recent post, the engagement metrics suggest a strong initial reception but a drop-off in sustained interaction. The sentiment analysis indicates a generally positive response, though some users expressed confusion about the product features.
                    </p>
                    <p style={{ lineHeight: '1.8', color: '#ccc' }}>
                        <strong>Recommendation:</strong> Create a follow-up post clarifying the features mentioned in the comments. Use the "Prediction" tool to test your draft before publishing.
                    </p>

                    <div style={{ marginTop: '30px' }}>
                        <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <FileAudio size={18} /> Download Audio Report
                        </button>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
