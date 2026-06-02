"use client";
import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Play, FileAudio, Loader2, CheckCircle2, Eye } from "lucide-react";
import { checkVideoStatus, checkVideoProgress } from "@/api";
import VideoPlayer from "@/components/VideoPlayer";

export default function Report() {
  const [ready, setReady] = useState(false);
  const [generating, setGenerating] = useState(true);
  const [progress, setProgress] = useState({ percent: 0, elapsed: 0, stage: "starting", frame: 0, total_frames: 0, speed: 0 });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const prog = await checkVideoProgress();
        setProgress(prog);

        const status = await checkVideoStatus();
        if (status.ready) {
          setReady(true);
          setGenerating(false);
          clearInterval(interval);
        } else {
          setGenerating(status.generating);
        }
      } catch {
        // ignore
      }
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ fontSize: "2rem", marginBottom: "30px" }}
      >
        AI <span className="gradient-text">Video Report</span>
      </motion.h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "30px" }}>
        {/* Video Player Panel */}
        <motion.div
          className="glass-panel"
          style={{
            padding: "20px",
            aspectRatio: ready ? "16/9" : "auto",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            background: "#000",
            position: "relative",
            overflow: "hidden",
            minHeight: ready ? "auto" : "350px",
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {ready ? (
            <VideoPlayer src="http://localhost:5001/api/video" />
          ) : generating ? (
            <div style={{ width: "100%", padding: "30px" }}>
              <div style={{ textAlign: "center", marginBottom: "25px" }}>
                <Loader2 className="animate-spin" size={48} color="var(--accent)" />
                <p style={{ margin: "15px 0 5px", fontWeight: 600, fontSize: "1.1rem" }}>Generating AI Video</p>
                <p style={{ margin: 0, fontSize: "0.85rem", opacity: 0.5, textTransform: "capitalize" }}>{progress.stage}</p>
              </div>

              {/* Progress bar */}
              <div style={{ height: "8px", borderRadius: "4px", background: "rgba(255,255,255,0.1)", overflow: "hidden", marginBottom: "12px" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(progress.percent, 100)}%` }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  style={{
                    height: "100%",
                    borderRadius: "4px",
                    background: "linear-gradient(90deg, var(--accent), #06b6d4)",
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", opacity: 0.5 }}>
                <span>{progress.percent.toFixed(1)}%</span>
                <span>{progress.elapsed}s elapsed</span>
                {progress.total_frames > 0 && (
                  <span>
                    {progress.frame}/{progress.total_frames} frames
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center" }}>
              <p style={{ opacity: 0.5 }}>No video being generated</p>
              <a href="/" style={{ color: "var(--accent)" }}>Analyze a post first</a>
            </div>
          )}
        </motion.div>

        {/* Info Panel */}
        <motion.div className="glass-panel" style={{ padding: "30px" }} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
          <h3 style={{ marginTop: 0, display: "flex", alignItems: "center", gap: "10px" }}>
            {ready ? <CheckCircle2 size={22} color="#22c55e" /> : <Loader2 className="animate-spin" size={22} color="var(--accent)" />}
            {ready ? "Video Ready" : "Processing"}
          </h3>

          {ready ? (
            <>
              <p style={{ lineHeight: "1.8", color: "#ccc" }}>
                Your AI-powered video montage is ready. It includes sentiment analysis, issue detection, and improvement suggestions synthesized into a narrated video report.
              </p>

              <div style={{ display: "flex", gap: "12px", marginTop: "25px", flexWrap: "wrap" }}>
                <a
                  href="http://localhost:5001/api/video"
                  download
                  style={{ textDecoration: "none", flex: 1 }}
                >
                  <button
                    className="btn-primary"
                    style={{ display: "flex", alignItems: "center", gap: "10px", width: "100%", justifyContent: "center" }}
                  >
                    <FileAudio size={18} /> Download Video
                  </button>
                </a>
              </div>
            </>
          ) : (
            <div>
              <p style={{ lineHeight: "1.8", color: "#ccc" }}>
                Your video is being assembled. This usually takes 2-5 minutes depending on the content length. Stay on this page or come back later.
              </p>
              <div style={{ marginTop: "20px", padding: "16px", borderRadius: "10px", background: "rgba(255,255,255,0.03)", border: "1px solid var(--card-border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "6px" }}>
                  <span style={{ opacity: 0.6 }}>Progress</span>
                  <span style={{ opacity: 0.6 }}>{progress.percent.toFixed(0)}%</span>
                </div>
                <div style={{ height: "4px", borderRadius: "2px", background: "rgba(255,255,255,0.1)", overflow: "hidden" }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(progress.percent, 100)}%` }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    style={{ height: "100%", borderRadius: "2px", background: "var(--accent)" }}
                  />
                </div>
                <div style={{ marginTop: "12px", display: "flex", gap: "16px", fontSize: "0.8rem", opacity: 0.5 }}>
                  <span>Stage: {progress.stage}</span>
                  <span>Elapsed: {progress.elapsed}s</span>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
