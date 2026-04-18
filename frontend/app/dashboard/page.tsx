"use client";
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import StatsCard from '@/components/Dashboard/StatsCard';
import SentimentChart from '@/components/Dashboard/SentimentChart';
import { ThumbsUp, MessageCircle, Share2, AlertTriangle, CheckCircle, Loader2, Play } from 'lucide-react';
import { checkVideoStatus } from '@/api';

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
  video_ready?: boolean;
}

export default function Dashboard() {
  const [post, setPost] = useState<PostData | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

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
        const parsedA = JSON.parse(a);
        setAnalysis(parsedA);
        setIsVideoReady(!!parsedA.video_ready);
      } catch (error) {
        console.error('Error parsing analysis data:', error);
      }
    }
  }, []);

  // Polling for video
  useEffect(() => {
    if (isVideoReady) return;

    const interval = setInterval(async () => {
      try {
        const status = await checkVideoStatus();
        if (status.ready) {
          setIsVideoReady(true);
          setIsGenerating(false);
          clearInterval(interval);
        } else {
          setIsGenerating(status.generating);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isVideoReady]);

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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <StatsCard title="Likes" value={post.likes} icon={ThumbsUp} color="34, 197, 94" />
        <StatsCard title="Comments" value={post.comments} icon={MessageCircle} color="59, 130, 246" />
        <StatsCard title="Shares" value={post.shares} icon={Share2} color="168, 85, 247" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 2 }}>
          <motion.div className="glass-panel" style={{ padding: '25px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h3 style={{ marginTop: 0, color: '#aaa' }}>Original Post</h3>
            <p style={{ fontSize: '1.1rem', lineHeight: '1.6' }}>{post.text}</p>
            <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
              {analysis?.topics?.map((t, i) => (
                <span key={i} style={{ background: 'rgba(255,255,255,0.1)', padding: '5px 10px', borderRadius: '20px', fontSize: '0.8rem' }}>#{t}</span>
              ))}
            </div>
          </motion.div>

          <motion.div className="glass-panel" style={{ padding: '25px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            <h3 style={{ marginTop: 0, color: '#aaa' }}>AI Insights</h3>
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#ef4444' }}>
                <AlertTriangle size={18} /> Issues Detected
              </h4>
              <ul style={{ paddingLeft: '20px', color: '#ddd' }}>
                {analysis?.issues && analysis.issues.length > 0 ? analysis.issues.map((issue, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{issue}</li>
                )) : <li>No critical issues found or analysis failed.</li>}
              </ul>
            </div>
            <div>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#22d3ee' }}>
                <CheckCircle size={18} /> Suggestions
              </h4>
              <ul style={{ paddingLeft: '20px', color: '#ddd' }}>
                {analysis?.suggestions?.map((s, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{s}</li>
                )) || <li>No suggestions available.</li>}
              </ul>
            </div>
          </motion.div>

          <motion.div className="glass-panel" style={{ padding: '25px' }} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
            <h3 style={{ marginTop: 0, color: '#aaa', marginBottom: '15px' }}>AI Video Report</h3>
            {isVideoReady ? (
              <video 
                controls 
                style={{ width: '100%', borderRadius: '10px', backgroundColor: '#000' }} 
                src="http://localhost:5001/api/video" 
                autoPlay
              />
            ) : (
              <div style={{ 
                height: '300px', 
                background: 'rgba(0,0,0,0.3)', 
                borderRadius: '10px', 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center',
                gap: '15px',
                border: '1px dashed rgba(255,255,255,0.1)'
              }}>
                <Loader2 className="animate-spin" size={40} color="#22d3ee" />
                <div style={{ textAlign: 'center' }}>
                  <p style={{ margin: 0, fontWeight: 'bold' }}>AI Montage is in progress...</p>
                  <p style={{ margin: 0, fontSize: '0.8rem', color: '#888' }}>Assembling frames and mixing audio (usually takes 1-2 mins)</p>
                </div>
              </div>
            )}
          </motion.div>
        </div>

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