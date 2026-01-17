"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart2, FileText, Home, CreditCard, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

export default function Navbar() {
    const pathname = usePathname();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const links = [
        { href: '/', label: 'Home', icon: Home },
        { href: '/subscription', label: 'Plans', icon: CreditCard },
        { href: '/dashboard', label: 'Dashboard', icon: BarChart2 },
        { href: '/report', label: 'AI Report', icon: FileText },
    ];

    const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass-panel nav-wrapper">
            <div className="container flex-nav">
                <Link href="/" style={{ textDecoration: 'none' }}>
                    <h1 className="gradient-text logo">SocialPulse</h1>
                </Link>

                {/* Desktop Links */}
                <div className="desktop-links">
                    {links.map((link) => {
                        const Icon = link.icon;
                        const isActive = pathname === link.href;

                        return (
                            <Link key={link.href} href={link.href} style={{ textDecoration: 'none', position: 'relative' }}>
                                <div className={`nav-link ${isActive ? 'active' : ''}`}>
                                    <Icon size={18} />
                                    <span>{link.label}</span>
                                    {isActive && (
                                        <motion.div
                                            layoutId="underline"
                                            className="nav-underline"
                                        />
                                    )}
                                </div>
                            </Link>
                        );
                    })}
                </div>

                {/* Mobile Menu Button */}
                <button className="mobile-menu-btn" onClick={toggleMenu}>
                    {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </div>

            {/* Mobile Menu Dropdown */}
            <AnimatePresence>
                {isMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mobile-dropdown"
                    >
                        <div className="mobile-links">
                            {links.map((link) => {
                                const Icon = link.icon;
                                const isActive = pathname === link.href;

                                return (
                                    <Link 
                                        key={link.href} 
                                        href={link.href} 
                                        onClick={() => setIsMenuOpen(false)}
                                        style={{ textDecoration: 'none' }}
                                    >
                                        <div className={`mobile-nav-link ${isActive ? 'active' : ''}`}>
                                            <Icon size={20} />
                                            <span>{link.label}</span>
                                        </div>
                                    </Link>
                                );
                            })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <style jsx>{`
                .nav-wrapper {
                    margin: 20px;
                    border-radius: 100px;
                    padding: 0 20px;
                }

                .flex-nav {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    height: 60px;
                }

                .logo {
                    font-size: 1.5rem;
                    fontWeight: bold;
                    margin: 0;
                }

                .desktop-links {
                    display: flex;
                    gap: 20px;
                }

                .nav-link {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: var(--foreground);
                    opacity: 0.7;
                    transition: opacity 0.3s, color 0.3s;
                    font-weight: 500;
                }

                .nav-link.active {
                    color: var(--primary);
                    opacity: 1;
                }

                .nav-underline {
                    position: absolute;
                    bottom: -20px;
                    left: 0;
                    right: 0;
                    height: 1.5px;
                    background: var(--primary);
                }

                .mobile-menu-btn {
                    display: none;
                    background: transparent;
                    border: none;
                    color: var(--foreground);
                    cursor: pointer;
                    padding: 5px;
                }

                .mobile-dropdown {
                    overflow: hidden;
                    background: rgba(10, 10, 10, 0.95);
                    backdrop-filter: blur(20px);
                    border-radius: 20px;
                    margin-top: 10px;
                    border: 1px solid var(--card-border);
                }

                .mobile-links {
                    display: flex;
                    flex-direction: column;
                    padding: 15px;
                    gap: 10px;
                }

                .mobile-nav-link {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 12px 15px;
                    border-radius: 12px;
                    color: var(--foreground);
                    opacity: 0.8;
                    transition: background 0.2s, opacity 0.2s;
                }

                .mobile-nav-link:hover, .mobile-nav-link.active {
                    background: var(--card-bg);
                    opacity: 1;
                    color: var(--primary);
                }

                @media (max-width: 850px) {
                    .desktop-links {
                        display: none;
                    }
                    .mobile-menu-btn {
                        display: block;
                    }
                    .nav-wrapper {
                        margin: 10px;
                        border-radius: 30px;
                    }
                }

                @media (max-width: 480px) {
                    .logo {
                        font-size: 1.2rem;
                    }
                    .nav-wrapper {
                        padding: 0 15px;
                    }
                }
            `}</style>
        </nav>
    );
}
