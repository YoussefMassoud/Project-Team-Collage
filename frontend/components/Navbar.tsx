"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Activity, BarChart2, FileText, Home } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Navbar() {
    const pathname = usePathname();

    const links = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/dashboard', label: 'Dashboard', icon: BarChart2 },
        { href: '/prediction', label: 'Prediction', icon: Activity },
        { href: '/report', label: 'AI Report', icon: FileText },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-panel" style={{ margin: '20px', borderRadius: '100px', padding: '0 20px' }}>
            <div className="container flex items-center justify-between" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '60px' }}>
                <Link href="/" style={{ textDecoration: 'none' }}>
                    <h1 className="gradient-text" style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: 0 }}>SocialPulse</h1>
                </Link>

                <div style={{ display: 'flex', gap: '20px' }}>
                    {links.map((link) => {
                        const Icon = link.icon;
                        const isActive = pathname === link.href;

                        return (
                            <Link key={link.href} href={link.href} style={{ textDecoration: 'none', position: 'relative' }}>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    color: isActive ? 'var(--primary)' : 'var(--foreground)',
                                    opacity: isActive ? 1 : 0.7,
                                    transition: 'opacity 0.3s'
                                }}>
                                    <Icon size={18} />
                                    <span style={{ fontWeight: 500 }}>{link.label}</span>
                                    {isActive && (
                                        <motion.div
                                            layoutId="underline"
                                            style={{
                                                position: 'absolute',
                                                bottom: '-20px',
                                                left: 0,
                                                right: 0,
                                                height: '2px',
                                                background: 'var(--primary)'
                                            }}
                                        />
                                    )}
                                </div>
                            </Link>
                        );
                    })}
                </div>
            </div>
        </nav>
    );
}
