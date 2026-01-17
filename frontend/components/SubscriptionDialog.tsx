"use client";
import React, { useState } from 'react';
import { X, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface SubscriptionDialogProps {
    isOpen: boolean;
    onClose: () => void;
    planName: string;
    planPrice: string;
}

export default function SubscriptionDialog({ isOpen, onClose, planName, planPrice }: SubscriptionDialogProps) {
    const [name, setName] = useState('');
    const [industry, setIndustry] = useState('');
    const [followers, setFollowers] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const phoneNumber = "201159304129";
        const text = `Hello, I am interested in the ${planName} - ${planPrice}%0A%0A` +
            `Client Details:%0A` +
            `- Name: ${name}%0A` +
            `- Business/Industry: ${industry}%0A` +
            `- Average Followers: ${followers}`;

        window.open(`https://wa.me/${phoneNumber}?text=${text}`, '_blank');
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    zIndex: 100,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backdropFilter: 'blur(8px)',
                    background: 'rgba(0, 0, 0, 0.6)'
                }}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="glass-panel"
                        style={{
                            width: '90%',
                            maxWidth: '500px',
                            padding: '30px',
                            position: 'relative',
                            background: '#0a0a0a',
                            border: '1px solid var(--card-border)'
                        }}
                    >
                        <button
                            onClick={onClose}
                            style={{
                                position: 'absolute',
                                top: '20px',
                                right: '20px',
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--foreground)',
                                cursor: 'pointer',
                                opacity: 0.7
                            }}
                        >
                            <X size={24} />
                        </button>

                        <h2 className="gradient-text" style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '10px' }}>
                            Get Started
                        </h2>
                        <p style={{ marginBottom: '25px', opacity: 0.8 }}>
                            You selected the <strong>{planName}</strong> plan for <span style={{ color: 'var(--primary)' }}>{planPrice}</span>.
                            Please fill in your details to proceed.
                        </p>

                        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Full Name</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="Enter your name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Business Model / Industry</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="e.g. E-commerce, Content Creator"
                                    value={industry}
                                    onChange={(e) => setIndustry(e.target.value)}
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Average Followers</label>
                                <input
                                    type="text"
                                    required
                                    className="input-field"
                                    placeholder="e.g. 10k, 1M"
                                    value={followers}
                                    onChange={(e) => setFollowers(e.target.value)}
                                />
                            </div>

                            <button
                                type="submit"
                                className="btn-primary"
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '10px',
                                    marginTop: '10px'
                                }}
                            >
                                <MessageCircle size={20} />
                                <span>Continue on WhatsApp</span>
                            </button>
                        </form>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
