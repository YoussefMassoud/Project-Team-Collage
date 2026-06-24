"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FileAudio, Loader2, CheckCircle2 } from "lucide-react";
import { checkVideoStatus, checkVideoProgress } from "@/api";
import VideoPlayer from "@/components/VideoPlayer";
import VideoLoadingPlayer from "@/components/VideoLoadingPlayer";

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
            padding: 0,
            background: "#000",
            position: "relative",
            overflow: "hidden",
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {ready ? (
            <VideoPlayer src="http://localhost:5001/api/video" />
          ) : (
            <VideoLoadingPlayer stage={generating ? progress.stage : "starting"} />
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
                Your video is being assembled. This usually takes 2–5 minutes. Stay on this page or come back later.
              </p>
              <p style={{ marginTop: "16px", fontSize: "0.85rem", color: "var(--accent)", textTransform: "capitalize", opacity: 0.8 }}>
                {progress.stage || "Starting…"}
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
