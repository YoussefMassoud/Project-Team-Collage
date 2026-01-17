"use client";
import React, { useState } from 'react';
import { Check } from 'lucide-react';
import SubscriptionDialog from '@/components/SubscriptionDialog';

const plans = [
  {
    duration: '3 Months',
    price: '450 EGP',
    description: 'Perfect for getting started',
    features: [
      'Social media Analytics',
      'ADS imporvment recommendations',
      'coustmer emotions digram',
      'AI Vedio Reports ',
      'AI ADS recommendations',
      'Coustmer feedback digram',
      'Coustmer support 24/7',
    ],
    highlight: false
  },
  {
    duration: '6 Months',
    price: '800 EGP',
    description: 'Most popular choice',
    features: [
     'Social media Analytics',
      'ADS imporvment recommendations',
      'coustmer emotions digram',
      'AI Vedio Reports ',
      'AI ADS recommendations',
      'Coustmer feedback digram',
      'Coustmer support 24/7',
    ],
    highlight: true
  },
  {
    duration: '1 Year',
    price: '1500 EGP',
    description: 'Best value for long term',
    features: [
      'Social media Analytics',
      'ADS imporvment recommendations',
      'coustmer emotions digram',
      'AI Vedio Reports ',
      'AI ADS recommendations',
      'Coustmer feedback digram',
      'Coustmer support 24/7',
    ],
    highlight: false
  }
];

export default function SubscriptionPage() {
  const [selectedPlan, setSelectedPlan] = useState<{ name: string, price: string } | null>(null);

  return (
    <div className="container" style={{ paddingTop: '100px', paddingBottom: '50px' }}>
      <div style={{ textAlign: 'center', marginBottom: '60px' }} className="animate-fade-in-down">
        <h1 className="gradient-text" style={{ fontSize: '3rem', fontWeight: 'bold', marginBottom: '20px' }}>
          Choose Your Plan
        </h1>
        <p style={{ color: 'var(--foreground)', opacity: 0.8, fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
          Unlock the full potential of SocialPulse with our flexible subscription options tailored to your needs.
        </p>
      </div>

      <div className="grid-responsive">
        {plans.map((plan, index) => (
          <div 
            key={index} 
            className="glass-panel animate-fade-in-up card-hover"
            style={{ 
              padding: '40px', 
              display: 'flex', 
              flexDirection: 'column',
              position: 'relative',
              transform: plan.highlight ? 'scale(1.05)' : 'scale(1)',
              zIndex: plan.highlight ? 10 : 1,
              border: plan.highlight ? '1px solid var(--primary)' : '1px solid var(--card-border)',
              boxShadow: plan.highlight ? '0 0 30px rgba(124, 58, 237, 0.2)' : 'none',
              animationDelay: `${index * 0.15}s`
            }}
          >
            {plan.highlight && (
              <div style={{
                position: 'absolute',
                top: '-15px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'var(--primary)',
                color: 'white',
                padding: '5px 15px',
                borderRadius: '20px',
                fontSize: '0.9rem',
                fontWeight: 'bold'
              }}>
                Best Value
              </div>
            )}

            <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '10px' }}>{plan.duration}</h2>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--primary)', marginBottom: '10px' }}>
              {plan.price}
            </div>
            <p style={{ marginBottom: '30px', opacity: 0.7 }}>{plan.description}</p>

            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 40px 0', flex: 1 }}>
              {plan.features.map((feature, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                  <Check size={20} color="var(--accent)" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            <button 
              className="btn-primary" 
              style={{ width: '100%', fontSize: '1.1rem' }}
              onClick={() => setSelectedPlan({ name: plan.duration, price: plan.price })}
            >
              Get Started
            </button>
          </div>
        ))}
      </div>

      <SubscriptionDialog 
        isOpen={!!selectedPlan} 
        onClose={() => setSelectedPlan(null)} 
        planName={selectedPlan?.name || ''} 
        planPrice={selectedPlan?.price || ''}
      />

      <style jsx>{`
        .grid-responsive {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 30px;
          align-items: center;
        }

        .animate-fade-in-down {
          animation: fadeInDown 0.8s ease-out forwards;
          opacity: 0;
        }

        .animate-fade-in-up {
          animation: fadeInUp 0.8s ease-out forwards;
          opacity: 0;
        }

        @keyframes fadeInDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .card-hover {
          transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card-hover:hover {
          transform: translateY(-10px) !important;
          border-color: var(--primary) !important;
          box-shadow: 0 10px 40px rgba(124, 58, 237, 0.2) !important;
        }
      `}</style>
    </div>
  );
}
