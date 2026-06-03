"use client";
import { useState } from 'react';
import { Check, MousePointerClick, FileText, MessageCircle, Trophy } from 'lucide-react';
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

      <div style={{ marginTop: '100px', textAlign: 'center', paddingBottom: '50px' }} className="animate-fade-in-up">
        <h2 className="gradient-text" style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '50px' }}>
          Steps to Subscribe
        </h2>
        
        <div className="flow-container">
          <div className="flow-step">
            <div className="icon-box"><MousePointerClick size={32} /></div>
            <h3>1. Choose Plan</h3>
            <p>Pick the best plan for your needs.</p>
          </div>
          
          <div className="flow-connector"></div>
          
          <div className="flow-step">
            <div className="icon-box"><FileText size={32} /></div>
            <h3>2. Fill Info</h3>
            <p>Enter your details in the form.</p>
          </div>
          
          <div className="flow-connector"></div>
          
          <div className="flow-step">
            <div className="icon-box"><MessageCircle size={32} /></div>
            <h3>3. Send to Support</h3>
            <p>Send the form via WhatsApp to our team.</p>
          </div>
          
          <div className="flow-connector"></div>
          
          <div className="flow-step">
            <div className="icon-box"><Trophy size={32} /></div>
            <h3>4. Success!</h3>
            <p>Congratulations! You are now subscribed.</p>
          </div>
        </div>
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

        .flow-container {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          max-width: 1000px;
          margin: 0 auto;
        }

        .flow-step {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
        }

        .icon-box {
          width: 70px;
          height: 70px;
          background: var(--card-bg);
          border: 1px solid var(--card-border);
          border-radius: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--primary);
          transition: all 0.3s ease;
        }

        .flow-step:hover .icon-box {
           background: var(--primary);
           color: white;
           transform: translateY(-5px);
           box-shadow: 0 10px 20px rgba(124, 58, 237, 0.3);
        }

        .flow-step h3 {
          font-size: 1.2rem;
          font-weight: 600;
          margin: 0;
        }

        .flow-step p {
          font-size: 0.9rem;
          opacity: 0.7;
          line-height: 1.4;
        }

        .flow-connector {
          flex: 0 0 40px;
          height: 2px;
          background: var(--card-border);
          margin-top: 35px;
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

        @media (max-width: 850px) {
          .flow-container {
            flex-direction: column;
            gap: 40px;
            align-items: center;
          }
          .flow-connector {
            width: 2px;
            height: 30px;
            margin-top: 0;
          }
        }

        @media (max-width: 768px) {
          .grid-responsive {
            grid-template-columns: 1fr;
            padding: 0 10px;
          }
          h1 {
            font-size: 2.2rem !important;
          }
          .glass-panel {
            padding: 30px !important;
            transform: scale(1) !important;
          }
        }
      `}</style>
    </div>
  );
}
