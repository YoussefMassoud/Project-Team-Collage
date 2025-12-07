"use client";
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import StatsCard from '@/components/Dashboard/StatsCard';
import SentimentChart from '@/components/Dashboard/SentimentChart';
import { ThumbsUp, MessageCircle, Share2, AlertTriangle, CheckCircle } from 'lucide-react';

interface PostData {
  text: string;
  likes: number;
  comments: number;
  shares: number;
}

interface AnalysisData {
  topics: string[];
  issues: string[];
  suggestions: string[];
  comment_analysis: {
    Positive: number;
    Negative: number;
    Neutral: number;
  };
  sentiment: 'Positive' | 'Negative' | 'Neutral';
}

export default function Dashboard() {
  const [post, setPost] = useState<PostData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);

  useEffect(() => {
    const p = localStorage.getItem('currentPost');
    const a = localStorage.getItem('currentAnalysis');
    if (p) {
      try {
        setPost(JSON.parse(p));
      } catch (error) {
        console.error('Error parsing post data:', error);
      }
    }
    if (a) {
      try {
        setAnalysis(JSON.parse(a));
      } catch (error) {
        console.error('Error parsing analysis data:', error);
      }
    }
  }, []);

  if (!post || !analysis) {
    return (
      <div className="container flex-center" style={{ minHeight: '50vh', flexDirection: 'column' }}>
        <p>No data found. Please analyze a post first.</p>
        <a href="/" className="btn-primary" style={{ marginTop: '20px', textDecoration: 'none' }}>Go Home</a>
      </div>
    );
  }

  return (
    <div className="container">
      <motion.h1
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        style={{ fontSize: '2rem', marginBottom: '30px' }}
      >
        Analysis <span className="gradient-text">Dashboard</span>
      </motion.h1>

      {/* Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <StatsCard title="Likes" value={post.likes} icon={ThumbsUp} color="34, 197, 94" />
        <StatsCard title="Comments" value={post.comments} icon={MessageCircle} color="59, 130, 246" />
        <StatsCard title="Shares" value={post.shares} icon={Share2} color="168, 85, 247" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Main Content & Issues */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 2 }}>

          {/* Post Content */}
          <motion.div className="glass-panel" style={{ padding: '25px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 style={{ marginTop: 0, color: '#aaa' }}>Original Post</h3>
            <p style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>{post.text}</p>
            <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
              {analysis.topics.map((t, i) => (
                <span key={i} style={{ background: 'rgba(255,255,255,0.1)', padding: '5px 10px', borderRadius: '20px', fontSize: '0.8rem' }}>#{t}</span>
              ))}
            </div>
          </motion.div>

          {/* Issues & Suggestions */}
          <motion.div className="glass-panel" style={{ padding: '25px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            <h3 style={{ marginTop: 0, color: '#aaa' }}>AI Insights</h3>

            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#ef4444' }}>
                <AlertTriangle size={18} /> Issues Detected
              </h4>
              <ul style={{ paddingLeft: '20px', color: '#ddd' }}>
                {analysis.issues.length > 0 ? analysis.issues.map((issue, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{issue}</li>
                )) : <li>No critical issues found.</li>}
              </ul>
            </div>

            <div>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#22d3ee' }}>
                <CheckCircle size={18} /> Suggestions
              </h4>
              <ul style={{ paddingLeft: '20px', color: '#ddd' }}>
                {analysis.suggestions.map((s, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{s}</li>
                ))}
              </ul>
            </div>
          </motion.div>

        </div>

        {/* Sidebar: Sentiment */}
        <motion.div className="glass-panel" style={{ padding: '25px', flex: 1 }} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h3 style={{ marginTop: 0, color: '#aaa', marginBottom: '20px' }}>Audience Sentiment</h3>
          <SentimentChart data={analysis.comment_analysis} />
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <p style={{ fontSize: '0.9rem', color: '#888' }}>Overall Tone</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: analysis.sentiment === 'Positive' ? '#22c55e' : analysis.sentiment === 'Negative' ? '#ef4444' : '#94a3b8' }}>
              {analysis.sentiment}
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}