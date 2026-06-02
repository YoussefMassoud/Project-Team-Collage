"use client";
import { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import { Loader2, MonitorPlay, CheckCircle2, AlertCircle } from "lucide-react";
import { checkVideoProgress } from "@/api";

interface ProgressData {
  percent: number;
  elapsed: number;
  stage: string;
  frame: number;
  total_frames: number;
  speed: number;
  stage_index: number;
  total_stages: number;
  ready: boolean;
  generating: boolean;
}

export default function VideoProgress({ onReady }: { onReady?: () => void }) {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [ready, setReady] = useState(false);
  const notified = useRef(false);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await checkVideoProgress();
        setProgress(data);

        if (data.ready && !ready) {
          setReady(true);
          if (!notified.current) {
            notified.current = true;
            onReady?.();
            // Browser notification
            if ("Notification" in window && Notification.permission === "granted") {
              new Notification("AI Video Report Ready", {
                body: "Your video montage has finished generating.",
                icon: "/favicon.ico",
              });
            }
          }
          clearInterval(interval);
        }
      } catch {
        // ignore polling errors
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [ready, onReady]);

  // Request notification permission
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  if (ready) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "12px",
          padding: "16px",
          borderRadius: "12px",
          background: "rgba(34, 197, 94, 0.1)",
          border: "1px solid rgba(34, 197, 94, 0.3)",
          color: "#22c55e",
        }}
      >
        <CheckCircle2 size={24} />
        <div>
          <p style={{ margin: 0, fontWeight: 600 }}>Video Ready</p>
          <p style={{ margin: 0, fontSize: "0.85rem", opacity: 0.7 }}>
            Completed in {progress?.elapsed || 0}s
          </p>
        </div>
      </motion.div>
    );
  }

  if (!progress || !progress.generating) {
    return null;
  }

  const stageNames = ["audio processing", "preparing assets", "generating audio", "building scenes", "rendering video"];
  const currentStage = stageNames[progress.stage_index - 1] || progress.stage;
  const pct = Math.min(progress.percent, 100);

  return (
    <div
      style={{
        padding: "20px",
        borderRadius: "12px",
        background: "rgba(0,0,0,0.3)",
        border: "1px solid var(--card-border)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
        <Loader2 className="animate-spin" size={20} color="var(--accent)" />
        <div style={{ flex: 1 }}>
          <p style={{ margin: 0, fontWeight: 600, fontSize: "0.95rem" }}>
            Generating AI Video Report
          </p>
          <p style={{ margin: 0, fontSize: "0.8rem", opacity: 0.6, textTransform: "capitalize" }}>
            {currentStage}
          </p>
        </div>
        <span style={{ fontSize: "0.85rem", opacity: 0.6, fontVariantNumeric: "tabular-nums" }}>
          {progress.elapsed}s
        </span>
      </div>

      {/* Progress bar */}
      <div
        style={{
          height: "6px",
          borderRadius: "3px",
          background: "rgba(255,255,255,0.1)",
          overflow: "hidden",
          marginBottom: "8px",
        }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
          style={{
            height: "100%",
            borderRadius: "3px",
            background: "linear-gradient(90deg, var(--accent), #06b6d4)",
          }}
        />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", opacity: 0.5 }}>
        <span>{pct.toFixed(1)}%</span>
        {progress.total_frames > 0 && (
          <span>
            Frame {progress.frame}/{progress.total_frames}
          </span>
        )}
        {progress.speed > 0 && <span>{progress.speed.toFixed(1)} it/s</span>}
      </div>
    </div>
  );
}
