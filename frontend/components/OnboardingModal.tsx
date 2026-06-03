"use client";
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    X, 
    Sparkles, 
    Link as LinkIcon, 
    Video, 
    CheckCircle2, 
    ArrowRight,
    PieChart,
    Smile} from 'lucide-react';

export default function OnboardingModal() {
    const [isVisible, setIsVisible] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);

    useEffect(() => {
        const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
        if (!hasSeenOnboarding) {
            const timer = setTimeout(() => setIsVisible(true), 1500); // Show after 1.5s
            return () => clearTimeout(timer);
        }
    }, []);

    const closeOnboarding = () => {
        setIsVisible(false);
        localStorage.setItem('hasSeenOnboarding', 'true');
    };

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            closeOnboarding();
        }
    };

    const steps = [
        {
            title: "Welcome to SocialPulse",
            description: "Analyze how people really feel about your posts using AI — in seconds.",
            buttonText: "Show Me How",
            icon: <Sparkles className="text-secondary" size={48} />,
            color: "var(--secondary)"
        },
        {
            title: "Paste Your Post URL",
            description: "Copy the link of any post from Facebook, Instagram, X, or TikTok and paste it in the analyze field.",
            buttonText: "Next Step",
            icon: <LinkIcon className="text-accent" size={48} />,
            color: "var(--accent)"
        },
        {
            title: "AI Emotion Analysis",
            description: "Our AI reads every comment and detects emotions automatically — no manual work or reading required.",
            buttonText: "Understood",
            icon: (
                <div className="flex gap-2">
                    <Smile className="text-primary" size={24} />
                    <Sparkles className="text-primary" size={24} />
                </div>
            ),
            color: "var(--primary)"
        },
        {
            title: "Understand Audience Emotions",
            description: "View clear charts showing satisfaction levels, frustration points, and overall sentiment distribution.",
            buttonText: "Continue",
            icon: <PieChart className="text-secondary" size={48} />,
            color: "var(--secondary)"
        },
        {
            title: "Watch Your AI Video Report",
            description: "Get a personalized AI video explaining what worked, what went wrong, and practical improvement steps.",
            buttonText: "Almost There",
            icon: <Video className="text-accent" size={48} />,
            color: "var(--accent)"
        },
        {
            title: "Ready to Analyze Your Post?",
            description: "Paste your link and let AI guide your next move. No technical skills required • Takes seconds.",
            buttonText: "Analyze Now",
            icon: <CheckCircle2 className="text-primary" size={48} />,
            color: "var(--primary)"
        }
    ];

    if (!isVisible) return null;

    return (
        <div className="onboarding-overlay">
            <AnimatePresence mode="wait">
                <motion.div 
                    key={currentStep}
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: -20 }}
                    className="onboarding-modal glass-panel"
                >
                    <button className="close-btn" onClick={closeOnboarding}>
                        <X size={20} />
                    </button>

                    <div className="step-content">
                        <div className="icon-wrapper" style={{ background: `rgba(255, 255, 255, 0.05)`, borderColor: steps[currentStep].color }}>
                            {steps[currentStep].icon}
                        </div>

                        <h2 className="gradient-text">{steps[currentStep].title}</h2>
                        <p>{steps[currentStep].description}</p>

                        <div className="progress-dots">
                            {steps.map((_, idx) => (
                                <div 
                                    key={idx} 
                                    className={`dot ${idx === currentStep ? 'active' : ''}`}
                                    style={{ background: idx === currentStep ? steps[currentStep].color : 'rgba(255, 255, 255, 0.1)' }}
                                />
                            ))}
                        </div>

                        <button 
                            className="btn-primary onboarding-cta"
                            onClick={nextStep}
                            style={{ width: '100%', marginTop: 'auto' }}
                        >
                            <span>{steps[currentStep].buttonText}</span>
                            <ArrowRight size={18} />
                        </button>

                        {currentStep === 0 && (
                            <button className="skip-btn" onClick={closeOnboarding}>
                                Skip tutorial
                            </button>
                        )}
                    </div>
                </motion.div>
            </AnimatePresence>

            <style jsx>{`
                .onboarding-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(8px);
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }

                .onboarding-modal {
                    max-width: 450px;
                    width: 100%;
                    background: #0a0a0a !important;
                    border: 1px solid var(--card-border);
                    padding: 40px;
                    position: relative;
                }

                .close-btn {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: transparent;
                    border: none;
                    color: white;
                    opacity: 0.4;
                    cursor: pointer;
                    transition: opacity 0.3s;
                }

                .close-btn:hover {
                    opacity: 1;
                }

                .step-content {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    min-height: 380px;
                }

                .icon-wrapper {
                    width: 80px;
                    height: 80px;
                    border-radius: 24px;
                    border: 1px solid;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 30px;
                }

                h2 {
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 20px;
                }

                p {
                    color: rgba(255, 255, 255, 0.7);
                    line-height: 1.6;
                    font-size: 1.05rem;
                    margin-bottom: 40px;
                    flex-grow: 1;
                }

                .onboarding-cta {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }

                .progress-dots {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 40px;
                }

                .dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 3px;
                    transition: all 0.3s ease;
                }

                .dot.active {
                    width: 24px;
                }

                .skip-btn {
                    margin-top: 20px;
                    background: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.4);
                    font-size: 0.9rem;
                    cursor: pointer;
                    text-decoration: underline;
                }

                .skip-btn:hover {
                    color: white;
                }

                @media (max-width: 480px) {
                    .onboarding-modal {
                        padding: 30px;
                    }
                    h2 {
                        font-size: 1.5rem;
                    }
                }
            `}</style>
        </div>
    );
}
