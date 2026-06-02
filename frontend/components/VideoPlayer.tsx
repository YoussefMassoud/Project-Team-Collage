"use client";
import { useRef, useState, useCallback, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX, Maximize, Minimize } from "lucide-react";
import { motion } from "framer-motion";

export default function VideoPlayer({ src }: { src: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const [ended, setEnded] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [muted, setMuted] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const hideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scheduleHide = useCallback(() => {
    setShowControls(true);
    if (hideTimer.current) clearTimeout(hideTimer.current);
    if (playing) {
      hideTimer.current = setTimeout(() => setShowControls(false), 2500);
    }
  }, [playing]);

  const togglePlay = useCallback(() => {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) { v.play(); setPlaying(true); setEnded(false); }
    else { v.pause(); setPlaying(false); }
    scheduleHide();
  }, [scheduleHide]);

  const seek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const v = videoRef.current;
    const bar = progressRef.current;
    if (!v || !bar) return;
    const rect = bar.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    v.currentTime = pct * (v.duration || 0);
  }, []);

  const toggleMute = useCallback(() => {
    const v = videoRef.current;
    if (!v) return;
    v.muted = !v.muted;
    setMuted(v.muted);
    scheduleHide();
  }, [scheduleHide]);

  const handleVolume = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const v = videoRef.current;
    if (!v) return;
    const val = parseFloat(e.target.value);
    v.volume = val;
    setVolume(val);
    setMuted(val === 0);
  }, []);

  const toggleFullscreen = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
      setFullscreen(false);
    } else {
      el.requestFullscreen();
      setFullscreen(true);
    }
    scheduleHide();
  }, [scheduleHide]);

  const formatTime = (s: number) => {
    if (isNaN(s)) return "0:00";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  useEffect(() => {
    const onFsChange = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onFsChange);
    return () => document.removeEventListener("fullscreenchange", onFsChange);
  }, []);

  const pct = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      onMouseMove={scheduleHide}
      onMouseLeave={() => playing && setShowControls(false)}
      style={{
        position: "relative",
        width: "100%",
        aspectRatio: "16 / 9",
        background: "#000",
        borderRadius: "12px",
        overflow: "hidden",
        cursor: showControls ? "default" : "none",
        userSelect: "none",
      }}
    >
      <video
        ref={videoRef}
        src={src}
        preload="metadata"
        onClick={togglePlay}
        onTimeUpdate={() => { const v = videoRef.current; if (v) { setCurrentTime(v.currentTime); setEnded(false); } }}
        onLoadedMetadata={() => { const v = videoRef.current; if (v) setDuration(v.duration); }}
        onEnded={() => { setPlaying(false); setEnded(true); setShowControls(true); }}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        style={{ width: "100%", height: "100%", display: "block", objectFit: "contain" }}
      />

      {/* Center play button (shown when paused or ended) */}
      {!playing && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={togglePlay}
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: ended ? "rgba(0,0,0,0.4)" : "rgba(0,0,0,0.15)",
            cursor: "pointer",
          }}
        >
          <motion.div
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.95 }}
            style={{
              width: "72px",
              height: "72px",
              borderRadius: "50%",
              background: "rgba(34, 211, 238, 0.9)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 40px rgba(34, 211, 238, 0.4)",
            }}
          >
            {ended ? (
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
            ) : (
              <Play size={28} fill="#000" style={{ marginLeft: 3 }} />
            )}
          </motion.div>
        </motion.div>
      )}

      {/* Bottom gradient + controls */}
      <motion.div
        initial={false}
        animate={{ opacity: showControls ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          background: "linear-gradient(transparent, rgba(0,0,0,0.85))",
          padding: "40px 16px 12px",
          pointerEvents: showControls ? "auto" : "none",
        }}
      >
        {/* Progress bar (scrubbable) */}
        <div
          ref={progressRef}
          onClick={seek}
          style={{
            height: "4px",
            borderRadius: "2px",
            background: "rgba(255,255,255,0.2)",
            cursor: "pointer",
            marginBottom: "10px",
            position: "relative",
          }}
        >
          <div
            style={{
              height: "100%",
              borderRadius: "2px",
              background: "var(--accent)",
              width: `${pct}%`,
              transition: "width 0.1s linear",
              position: "relative",
            }}
          >
            <div
              style={{
                position: "absolute",
                right: "-6px",
                top: "-4px",
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                background: "var(--accent)",
                boxShadow: "0 0 6px rgba(34,211,238,0.6)",
              }}
            />
          </div>
        </div>

        {/* Controls row */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {/* Play/Pause */}
          <button onClick={togglePlay} style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", padding: 4, display: "flex" }}>
            {playing ? <Pause size={20} /> : <Play size={20} fill="#fff" />}
          </button>

          {/* Time */}
          <span style={{ fontSize: "0.8rem", opacity: 0.7, fontVariantNumeric: "tabular-nums", minWidth: "80px" }}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>

          {/* Spacer */}
          <div style={{ flex: 1 }} />

          {/* Volume */}
          <button onClick={toggleMute} style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", padding: 4, display: "flex" }}>
            {muted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={muted ? 0 : volume}
            onChange={handleVolume}
            style={{
              width: "64px",
              height: "4px",
              accentColor: "var(--accent)",
              cursor: "pointer",
            }}
          />

          {/* Fullscreen */}
          <button onClick={toggleFullscreen} style={{ background: "none", border: "none", color: "#fff", cursor: "pointer", padding: 4, display: "flex" }}>
            {fullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
