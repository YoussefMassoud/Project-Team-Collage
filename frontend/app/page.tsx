"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { fetchPost, analyzePost } from '@/api';
import { Search, Loader2 } from 'lucide-react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAnalyze = async () => {
    if (!url) return;
    setLoading(true);
    try {
      // 1. Fetch Post Data
      const postRes = await fetchPost(url);

      // Check if we got a valid post object (checking for a key like 'text' or 'post_id')
      if (postRes && !postRes.message) {
        localStorage.setItem('currentPost', JSON.stringify(postRes));

        // 2. Analyze Post
        const analysisRes = await analyzePost(postRes);
        localStorage.setItem('currentAnalysis', JSON.stringify(analysisRes));

        // 3. Redirect
        router.push('/dashboard');
      } else {
        alert("Failed to fetch post: " + (postRes.message || "Unknown error"));
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to analyze post. Please check the backend connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container flex-center" style={{ minHeight: '80vh', flexDirection: 'column', textAlign: 'center' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 style={{ fontSize: '4rem', fontWeight: '800', marginBottom: '20px', lineHeight: 1.1 }}>
          Unlock Your <br />
          <span className="gradient-text">Social Potential</span>
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#888', marginBottom: '40px', maxWidth: '600px', margin: '0 auto 40px' }}>
          Paste your post link below to get AI-powered insights, sentiment analysis, and improvement suggestions instantly.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="glass-panel"
        style={{ padding: '10px', display: 'flex', gap: '10px', width: '100%', maxWidth: '600px' }}
      >
        <div style={{ position: 'relative', flex: 1 }}>
          <Search style={{ position: 'absolute', left: '12px', top: '12px', color: '#666' }} size={20} />
          <input
            type="text"
            placeholder="Paste post URL (Facebook, Instagram, X, TikTok)..."
            className="input-field"
            style={{ paddingLeft: '40px', background: 'transparent', border: 'none' }}
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
        </div>
        <button
          className="btn-primary"
          onClick={handleAnalyze}
          disabled={loading}
          style={{ minWidth: '140px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Analyze Now'}
        </button>
      </motion.div>

      <div style={{ marginTop: '60px', display: 'flex', gap: '40px', opacity: 0.5 }}>
        <span>Facebook</span>
        <span>Instagram</span>
        <span>X (Twitter)</span>
        <span>TikTok</span>
      </div>
    </div>
  );
}
