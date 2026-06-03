"use client";
import { Phone, Instagram } from 'lucide-react';

export default function Footer() {
    return (
        <footer className="footer-area">
            <div className="container footer-content">
                <div className="footer-links">
                    <a href="tel:01159304129" className="footer-icon-btn" title="Call Support: 01159304129">
                        <Phone size={24} />
                    </a>
                    <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="footer-icon-btn" title="Follow us on Instagram">
                        <Instagram size={24} />
                    </a>
                </div>
                <p className="copyright">&copy; 2024 SocialPulse. All rights reserved.</p>
            </div>

            <style jsx>{`
                .footer-area {
                    position: relative;
                    padding: 30px 0;
                    margin-top: 50px;
                    overflow: hidden;
                    border-top: 1px solid var(--card-border);
                    background: linear-gradient(-45deg, #0a0a0a, #1a0b2e, #0a0a0a, #0d1a1a);
                    background-size: 400% 400%;
                    animation: gradientBG 15s ease infinite;
                }

                @keyframes gradientBG {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }

                .footer-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                    z-index: 1;
                    position: relative;
                }

                .footer-links {
                    display: flex;
                    gap: 30px;
                }

                .footer-icon-btn {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 45px;
                    height: 45px;
                    background: var(--card-bg);
                    border: 1px solid var(--card-border);
                    border-radius: 50%;
                    color: var(--foreground);
                    opacity: 0.8;
                    text-decoration: none;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }

                .footer-icon-btn:hover {
                    opacity: 1;
                    color: var(--primary);
                    background: var(--glass);
                    border-color: var(--primary);
                    transform: translateY(-5px) scale(1.1);
                    box-shadow: 0 5px 15px rgba(124, 58, 237, 0.3);
                }

                .copyright {
                    font-size: 0.85rem;
                    opacity: 0.5;
                    margin: 0;
                }

                @media (max-width: 600px) {
                    .footer-links {
                        flex-direction: column;
                        align-items: center;
                        gap: 15px;
                    }
                    .footer-area {
                        padding: 40px 0;
                    }
                }
            `}</style>
        </footer>
    );
}
